from viktor.core import ViktorController


class CalculationFolderController(ViktorController):
    label = 'Calculation folder'
    children = ['Calculation']
    show_children_as = 'Cards'  # or 'Table'
