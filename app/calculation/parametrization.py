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
from viktor.parametrization import Parametrization, Tab, Section, NumberField, \
    LineBreak, BooleanField, DownloadButton


class CalculationParametrization(Parametrization):

    general = Tab('General')
    general.beam = Section('Beam')
    general.beam.length = NumberField('Length (L)', suffix='mm', default=100)
    general.beam.width = NumberField('Width (W)', suffix='mm', default=10)
    general.beam.height = NumberField('Height (H)', suffix='mm', default=10)
    general.beam.E = NumberField('Modulus of Elasticity (E)', default=200000, suffix='N/mm2')

    general.loads = Section('Loads')
    general.loads.aw = NumberField('Starting point of load (aw)', suffix='mm', default=9)
    general.loads.nl = LineBreak()
    general.loads.wa = NumberField('Distributed load amplitude (wa)', suffix='N/mm', flex=40, default=5)
    general.loads.wL = NumberField('Distributed load amplitude (wL)', suffix='N/mm', flex=40, default=5)

    visualization = Tab('Visualization')
    visualization.axis_system = Section('Axis system')
    visualization.axis_system.show_axis_system = BooleanField('Visualize axes', default=True)

    downloads = Tab('Downloads')
    downloads.calculation_sheet = Section('Calculation sheet')
    downloads.calculation_sheet.btn = DownloadButton('Download', 'download_spreadsheet')
