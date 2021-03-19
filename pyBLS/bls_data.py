"""
by: Aaron Finocchiaro
APCV 498 - Senior Capstone

A class designed to interact with the bls.gov API.
"""
import json
import os
import re
import pandas as pd
import requests
from pybls import qcew_area_codes_df, oes_area_codes_df


BLS_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'

#set plotting backend to plotly
pd.options.plotting.backend = "plotly"

class BlsData():
    """
    A class designed to interact with the Bureau of Labor Statistics public API and 
    translate the data into a Pandas Dataframe.
    """
    def __init__(self, series_ids:list, start_year:int, end_year:str, raw_data=None):

        self.series_ids = series_ids
        self.start_year = start_year
        self.end_year = end_year

        self.raw_data = raw_data if raw_data else self._request_bls_data()

        self.df = self._construct_df()
        self.locations = self._get_location()

    @classmethod
    def from_json(cls, json_file:str):
        """
        Alternate constructor for BlsData that takes a json file of data returned from the BLS
        API and uses it to create a BlsData object.
        """
        #read file
        with open(json_file, 'r') as json_file:
            data = json.load(json_file)

        #construct seriesID list
        series_ids = [series['seriesID'] for series in data]

        #get start year from last data point in data
        start_year = data[-1]['data'][-1]['year']

        #get end year from first data point in data
        end_year = data[0]['data'][0]['year']

        return cls(series_ids=series_ids, start_year=start_year, end_year=end_year, raw_data=data)

    def _request_bls_data(self):
        headers = {
            'content-type' : 'application/json',
        }
        data = json.dumps({
            "seriesid" : self.series_ids,
            "startyear" : self.start_year,
            "endyear" : self.end_year,
            "catalog" : False,
            "annualaverage" : False,
            "aspects" : False,
            "registrationKey" : os.environ.get('BLS_API_KEY'),
        })

        #make post request
        response = requests.post(BLS_URL, data=data, headers=headers)

        return response.json()['Results']['series']

    def _construct_df(self) -> pd.DataFrame:
        """
        Constructs a pandas dataframe from the raw data returned from the BLS
        API.
        Returns a dataframe organized by the data frequency in organize_df()
        """
        #make an empty dataframe with desired cols
        cols = ['year', 'period']
        bls_df = pd.DataFrame(columns=cols)

        #use for loop to create df
        for bls_series in self.raw_data:
            series_df = pd.DataFrame(bls_series['data'])
            series_df = series_df[cols + ['value']]
            series_df['value'] = pd.to_numeric(series_df['value'])
            series_df = series_df.rename(columns={'value' : bls_series['seriesID']})
            bls_df = bls_df.merge(right=series_df, on=['year', 'period'], how='outer')

        return self.organize_df(bls_df)

    def organize_df(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Organizes pandas dataframe depending on the term of the data.
        Currently works for monthly and quarterly data.
        Returns a pandas dataframe.
        """
        #quarterly data
        if df.loc[0]['period'][0] == 'Q':
            df['period'] = df['period'].str.replace('0', '')
            df['date'] = df['year'].map(str)+ '-' +df['period'].map(str)
            df['date'] = pd.to_datetime(df['date'])

        #monthly data
        if df.loc[0]['period'][0] == 'M':
            df['period'] = df['period'].str.replace('M', '')
            df['date'] = df['period'].map(str)+ '-' +df['year'].map(str)
            df['date'] = pd.to_datetime(df['date'], format='%m-%Y')

        #annual data
        if df.loc[0]['period'][0] == 'A':
            df = df.rename(columns={'year':'date'}, errors='raise')

        #change index and sort
        df = df.set_index('date')
        df = df.sort_index()

        #drop extra cols
        df = df.drop(columns=['period', 'year'], errors='ignore')

        return df

    def write_to_json(self, file_name:str):
        """
        Writes raw data from BLS API out to a json file to avoid having to re-query
        the API for testing.
        """
        with open(f"{file_name.split('.')[0]}.json", 'w') as json_out:
            json.dump(self.raw_data, json_out, indent=4)

    def create_graph(self, title:str, graph_type:str, clean_names:bool=True,
            custom_column_names:dict=None, transpose:bool=False):
        """
        Returns a graph-able plotly object from the given data and constructed
        dataframe. Renames columns based on the mapping of seriesIDs to locations
        from the BLS area codes.
        Arguments:
            - title = str; graph title
            - clean_names = bool; replace seriesIDs in df columns with location name
            - custom_column_names = dict; mapping of seriesID to custom defined column names
            - transpose = bool; transpose df to graph correctly
        Returns a plotly object.
        """
        #check graph type
        accepted_graphs = ['line', 'bar']
        if graph_type not in accepted_graphs:
            raise ValueError(f"Invalid graph type. Expected one of: {', '.join(accepted_graphs)}")

        plotting_df = self.df

        #replace column names with location names
        if clean_names and not custom_column_names:
            plotting_df = plotting_df.rename(columns=self.locations, errors="raise")

        #replace column names with a custom name
        if clean_names and custom_column_names:
            if not isinstance(custom_column_names, dict):
                raise TypeError("Custom column names must be of type dict.")
            plotting_df = plotting_df.rename(columns=custom_column_names, errors="raise")

        #transpose df, typically if length is 1
        if transpose:
            plotting_df = plotting_df.transpose()

        #bar graph
        if graph_type == 'bar':
            return plotting_df.plot.bar(title = title, template="simple_white")

        #line graph
        return plotting_df.plot(title = title, template="simple_white")

    def _get_location(self):
        """
        Uses the area_titles.csv file from https://data.bls.gov/cew/doc/titles/area/area_titles.htm
        to create a dataframe of all area_codes that BLS uses. This returns a dict with the series
        IDs as keys and the location name as values.
        """
        series_id_locations = {}
        for series in self.series_ids:
            if re.match('[EN|LA]', series[0:2]):
                if series[0:2] == 'EN':
                    area_code = re.search(r'^[A-Z]{3}([\d|U][\d|S]\d\d\d)', series).group(1)
                if series[0:2] == 'LA':
                    area_code = re.search(r'^[A-Z]{5}(\d\d\d\d\d)', series).group(1)
                series_id_locations[series] = qcew_area_codes_df.loc[area_code]['area_title']
            if re.match('OE', series[0:2]):
                area_code = re.search(r'^[A-Z]*(\d\d\d\d\d\d\d)', series).group(1)
                series_id_locations[series] = oes_area_codes_df.loc[area_code]['area_name']

        return series_id_locations
