from pathlib import Path
import pandas as pd
import plotly.express as px

import viktor as vkt


class Parametrization(vkt.ViktorParametrization):
    beam = vkt.Section('Beam')
    beam.schematic = vkt.Image(path="beam_schematic.png")
    beam.length = vkt.NumberField('Length (L)', suffix='mm', default=80, max=100)
    beam.width = vkt.NumberField('Width (W)', suffix='mm', default=10)
    beam.height = vkt.NumberField('Height (H)', suffix='mm', default=10)
    beam.E = vkt.NumberField('Modulus of Elasticity (E)', default=200000, suffix='N/mm2')

    loads = vkt.Section('Loads')
    loads.aw = vkt.NumberField('Starting point of load (aw)', suffix='mm', default=9, flex=50)
    loads.lb = vkt.LineBreak()
    loads.wa = vkt.NumberField('Distributed load amplitude (wa)', suffix='N/mm', flex=50, default=5)
    loads.wL = vkt.NumberField('Distributed load amplitude (wL)', suffix='N/mm', flex=50, default=5)

    calculation_sheet = vkt.Section('Download')
    calculation_sheet.button = vkt.DownloadButton('Download', method='download_spreadsheet')


class Controller(vkt.ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization

    @staticmethod
    def get_evaluated_spreadsheet(params):
        inputs = [
            vkt.spreadsheet.SpreadsheetCalculationInput('L', params.beam.length),
            vkt.spreadsheet.SpreadsheetCalculationInput('W', params.beam.width),
            vkt.spreadsheet.SpreadsheetCalculationInput('H', params.beam.height),
            vkt.spreadsheet.SpreadsheetCalculationInput('E', params.beam.E),
            vkt.spreadsheet.SpreadsheetCalculationInput('aw', params.loads.aw),
            vkt.spreadsheet.SpreadsheetCalculationInput('wa', params.loads.wa),
            vkt.spreadsheet.SpreadsheetCalculationInput('wL', params.loads.wL)
        ]
        sheet_path = Path(__file__).parent / 'beam_calculation.xls'
        sheet = vkt.spreadsheet.SpreadsheetCalculation.from_path(sheet_path, inputs=inputs)
        result = sheet.evaluate(include_filled_file=True)
        return result

    @vkt.PlotlyAndDataView('Results', duration_guess=1)
    def get_data_view(self, params, **kwargs):
        result = self.get_evaluated_spreadsheet(params)

        evaluated_file = vkt.File.from_data(result.file_content)
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
        data = vkt.DataGroup(
            maximum_deflection=vkt.DataItem(
                'Maximum Deflection',
                max_deflection,
                suffix='microns',
                number_of_decimals=2
            ),
            maximum_bending_stress=vkt.DataItem(
                'Maximum bending stress',
                max_bending_stress,
                suffix='N/mm2',
                number_of_decimals=2
            ),
        )
        return vkt.PlotlyAndDataResult(fig.to_json(), data)

    def download_spreadsheet(self, params, **kwargs):
        result = self.get_evaluated_spreadsheet(params)
        return vkt.DownloadResult(result.file_content, 'evaluated_beam.xlsx')
