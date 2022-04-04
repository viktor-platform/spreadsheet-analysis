"""Copyright (c) 2022 VIKTOR B.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

VIKTOR B.V. PROVIDES THIS SOFTWARE ON AN "AS IS" BASIS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from pathlib import Path

from viktor.core import ViktorController
from viktor.external.spreadsheet import SpreadsheetCalculation
from viktor.external.spreadsheet import SpreadsheetCalculationInput
from viktor.geometry import CartesianAxes
from viktor.geometry import Point
from viktor.geometry import SquareBeam
from viktor.result import DownloadResult
from viktor.views import DataGroup
from viktor.views import DataItem
from viktor.views import DataResult
from viktor.views import DataView
from viktor.views import GeometryResult
from viktor.views import GeometryView
from viktor.views import SVGResult
from viktor.views import SVGView

from .parametrization import CalculationParametrization


class CalculationController(ViktorController):
    label = 'Unique Calculation'
    parametrization = CalculationParametrization

    viktor_convert_entity_field = True

    def get_evaluated_spreadsheet(self, params):
        inputs = [
            SpreadsheetCalculationInput('L', params['general']['beam']['length']),
            SpreadsheetCalculationInput('W', params['general']['beam']['width']),
            SpreadsheetCalculationInput('H', params['general']['beam']['height']),
            SpreadsheetCalculationInput('E', params['general']['beam']['E']),
            SpreadsheetCalculationInput('aw', params['general']['loads']['aw']),
            SpreadsheetCalculationInput('wa', params['general']['loads']['wa']),
            SpreadsheetCalculationInput('wL', params['general']['loads']['wL']),
        ]
        sheet_path = Path(__file__).parent / 'beam_calculation.xls'
        sheet = SpreadsheetCalculation.from_path(sheet_path, inputs=inputs)
        result = sheet.evaluate(include_filled_file=True)

        return result

    @DataView('Results', duration_guess=1)
    def get_data_view(self, params, **kwargs):
        result = self.get_evaluated_spreadsheet(params)

        max_deflection = result.values['maximum_deflection']
        max_bending_stress = result.values['maximum_bending_stress']
        data = DataGroup(
            maximum_deflection=DataItem('Maximum deflection', max_deflection, suffix='microns', number_of_decimals=2),
            maximum_bending_stress=DataItem('Maximum bending stress', max_bending_stress, suffix='N/mm2', number_of_decimals=2),
        )

        return DataResult(data)

    @SVGView('Schematic', duration_guess=1)
    def get_svg_view(self, params, **kwargs):
        img_path = Path(__file__).parent / 'beam_schematic.svg'
        return SVGResult.from_path(img_path)

    @GeometryView('3D', duration_guess=1)
    def get_3d_view(self, params, **kwargs):
        length_x = params['general']['beam']['length']
        length_y = params['general']['beam']['width']
        length_z = params['general']['beam']['height']

        beam = SquareBeam(length_x, length_y, length_z)

        axis_system_location = Point(- 0.5 * length_x - max(length_y, length_z) * 1.2, 0, 0)
        axis_system = CartesianAxes(axis_system_location, axis_length=5, axis_diameter=0.5)

        if params['visualization']['axis_system']['show_axis_system']:
            geometries = [beam, axis_system]
        else:
            geometries = [beam]

        return GeometryResult(geometries)

    def download_spreadsheet(self, params, **kwargs):
        result = self.get_evaluated_spreadsheet(params)
        return DownloadResult(result.file_content, 'evaluated_beam.xlsx')
