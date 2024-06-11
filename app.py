from pathlib import Path
import pandas as pd
import plotly.express as px

from viktor import ViktorController, File
from viktor.parametrization import ViktorParametrization, NumberField, Section, LineBreak, Image, DownloadButton
from viktor.external.spreadsheet import SpreadsheetCalculation, SpreadsheetCalculationInput
from viktor.views import DataGroup, DataItem, PlotlyAndDataView, PlotlyAndDataResult
from viktor.result import DownloadResult


class Parametrization(ViktorParametrization):
    beam = Section('Beam')
    beam.schematic = Image(path="beam_schematic.png")
    beam.length = NumberField('Length (L)', suffix='mm', default=80, max=100)
    beam.width = NumberField('Width (W)', suffix='mm', default=10)
    beam.height = NumberField('Height (H)', suffix='mm', default=10)
    beam.E = NumberField('Modulus of Elasticity (E)', default=200000, suffix='N/mm2')

    loads = Section('Loads')
    loads.aw = NumberField('Starting point of load (aw)', suffix='mm', default=9, flex=50)
    loads.lb = LineBreak()
    loads.wa = NumberField('Distributed load amplitude (wa)', suffix='N/mm', flex=50, default=5)
    loads.wL = NumberField('Distributed load amplitude (wL)', suffix='N/mm', flex=50, default=5)

    calculation_sheet = Section('Download')
    calculation_sheet.button = DownloadButton('Download', method='download_spreadsheet')


class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization

    @staticmethod
    def get_evaluated_spreadsheet(params):
        inputs = [
            SpreadsheetCalculationInput('L', params.beam.length),
            SpreadsheetCalculationInput('W', params.beam.width),
            SpreadsheetCalculationInput('H', params.beam.height),
            SpreadsheetCalculationInput('E', params.beam.E),
            SpreadsheetCalculationInput('aw', params.loads.aw),
            SpreadsheetCalculationInput('wa', params.loads.wa),
            SpreadsheetCalculationInput('wL', params.loads.wL)
        ]
        sheet_path = Path(__file__).parent / 'beam_calculation.xls'
        sheet = SpreadsheetCalculation.from_path(sheet_path, inputs=inputs)
        result = sheet.evaluate(include_filled_file=True)
        return result

    @PlotlyAndDataView('Results', duration_guess=1)
    def get_data_view(self, params, **kwargs):
        result = self.get_evaluated_spreadsheet(params)

        evaluated_file = File.from_data(result.file_content)
        with evaluated_file.open_binary() as fp:
            data_df = pd.read_excel(fp, sheet_name='Data')
        deflection_data = data_df['Deflection (microns)'].head(params.beam.length + 1)
        fig = px.line(
            deflection_data,
            title='Beam deflection',
            labels={'value': 'Deflection (microns)', 'index': 'Length (mm)'}
        )

        max_deflection = result.values['maximum_deflection']
        max_bending_stress = result.values['maximum_bending_stress']
        data = DataGroup(
            maximum_deflection=DataItem(
                'Maximum Deflection',
                max_deflection,
                suffix='microns',
                number_of_decimals=2
            ),
            maximum_bending_stress=DataItem(
                'Maximum bending stress',
                max_bending_stress,
                suffix='N/mm2',
                number_of_decimals=2
            ),
        )
        return PlotlyAndDataResult(fig.to_json(), data)

    def download_spreadsheet(self, params, **kwargs):
        result = self.get_evaluated_spreadsheet(params)
        return DownloadResult(result.file_content, 'evaluated_beam.xlsx')
