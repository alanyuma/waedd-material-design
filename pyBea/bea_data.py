"""
Interacts with the Bureau of Economic Analysis API with python.

By: Aaron Finocchiaro
"""
import os
import urllib.parse as urlparse
import pandas as pd
import requests

BEA_API_URL = "http://apps.bea.gov/api/data?"

def request_bea_data(params:list) -> dict:
    """
    Creates query url and submits request to BEA API endpoint.
    Arguments:
        - params; a list of query parameters to include in the request.
    Returns dict
    """
    params.update({
        'UserID' : os.environ.get('BEA_API_KEY'),
        'method' : 'GetData',
        'ResultFormat' : 'JSON',
    })
    url_parts = list(urlparse.urlparse(BEA_API_URL))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlparse.urlencode(query)

    results = requests.get(urlparse.urlunparse(url_parts))
    return results.json()

class NIdata():
    """
    Retrieves and organizes NIPA BEA data into a pandas dataframe.
    Parameters:
    TableName = str; Either NIPA or NIUnderlyingDetail
    frequency = list; a list accepting values 'a', 'y', 'q' defining the frequency of data requested.
    table_name = str; income or employment table to request.
    year = list; a list of years to request data from.
    """
    def __init__(self, dataset_name:str, frequency:list, table_name:str, years:list):

        self.dataset_name = self._is_valid_dataset_name(dataset_name)
        self.frequency = self._is_valid_frequency(frequency)
        self.table_name = table_name
        self.years = years
        self.query_params = {
            'datasetname' : 'NIPA',
            'frequency' : ','.join(self.frequency),
            'TableName' : self.table_name,
            'Year' : ','.join(self.years),
        }
        self.raw_data = request_bea_data(self.query_params)
        self.df = pd.DataFrame(self.raw_data['BEAAPI']['Results']['Data'])

    def _is_valid_dataset_name(self, table):
        if table.lower() not in ['nipa', "niunderlyingdetail"]:
            raise ValueError(f"{table} is not a valid table for NIdata, use either 'NIPA' or 'NIUnderlyingDetail'.")
        return table

    def _is_valid_frequency(self, frequency):
        for term in frequency:
            if term.lower() not in ['a', 'm', 'q']:
                raise ValueError(f"{term} is not a valid table for frequency, use a-annual, q-quarterly, or m-monthly.")
        return frequency

class regionalData():
    """
    Retrieves and organizes regional BEA data into a pandas dataframe.
    Parameters:
    table_name = str; income or employment table to request
    line_code = int; a specific line in the requested table to get
    geo_fips = list; a list of integers for a specific city, town, MSA, MIC, County, CSA, or state.
               also takes:
               COUNTY = all counties
               STATE = all states
               MSA = all MSAs
               MIC = all MICs
               PORT = all state metro/nonmetro portions
               DIV = all metro divisions
               CSA = all CSAs
               any state abbreviation = all counties in a specific state
    year = list; a list of years to request data from
    """

    def __init__(self, table_name:str, line_code:int, geo_fips:list, years:list):

        self.table_name = table_name
        self.line_code = line_code
        self.geo_fips = geo_fips
        self.years = years
        self.params = {
            'datasetname' : 'Regional',
            'TableName' : self.table_name,
            'LineCode' : self.line_code,
            'GeoFIPS' : ','.join(self.geo_fips),
            'Year' : ','.join(self.years),
        }

        self.raw_data = request_bea_data(self.params)
        self.raw_df = pd.DataFrame(self.raw_data['BEAAPI']['Results']['Data'])
        self.df = self._clean_df()

    def _clean_df(self):
        """
        Clean the raw dataframe and make it into an easily parsible dataframe.
        """
        #deep copy to avoid overwriting
        clean_df = self.raw_df.copy()

        #strip off asterisks from GeoName col
        clean_df['GeoName'] = clean_df['GeoName'].map(lambda x: x.rstrip(r'\*'))

        #organize the df
        clean_df = clean_df.pivot(index='TimePeriod', columns='GeoName')['DataValue']

        return clean_df
