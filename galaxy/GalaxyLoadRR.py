from ParamExecClass import ParamExecClass
from pyHRV.Files import load_rr, save_data_series


class GalaxyLoadRR(ParamExecClass):
    """
    kwargs['input'] ----> input file
    kwargs['output'] ---> output file
    kwargs['column'] ---> column to load
                 default: PyHRVSettings.load_rr_column_name
    """

    def execute(self):
        input_file = self._kwargs['input']
        output_file = self._kwargs['output']
        column = self._kwargs['column']

        save_data_series(load_rr(input_file, column=column), output_file)