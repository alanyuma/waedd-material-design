"""
by: Aaron Finocchiaro
APCV 498 - Senior Capstone

A class designed to interact with the bls.gov API.
"""
import json
import os
import re
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from pybls import la_area_codes_df, oes_area_codes_df, qcew_area_codes_df


BLS_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'

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

        self.raw_df = self._construct_df()
        self.df = self._organize_df()
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

    def _request_bls_data(self) -> list:
        """
        Not meant to be called outside of __init__. This method handles the API call to the BLS API
        based on the given attributes.
        Returns a list containing the raw results from the BLS api call.
        """
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
        Returns a pandas dataframe
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

        return bls_df

    def _organize_df(self) -> pd.DataFrame:
        """
        Organizes pandas dataframe depending on the term of the data.
        Currently works for monthly, quarterly, and annual data.
        Returns a pandas dataframe.
        """
        #Deep copy the raw dataframe to avoid overwriting it
        df = self.raw_df.copy()

        #quarterly data
        if df.loc[0]['period'][0] == 'Q':
            df['period'] = df['period'].str.replace('0', '')
            df['date'] = df['year'].map(str)+ '-' +df['period'].map(str)
            df['date'] = pd.to_datetime(df['date']).apply(lambda x: x.strftime('%Y-%m'))

        #monthly data
        if df.loc[0]['period'][0] == 'M':
            df['period'] = df['period'].str.replace('M', '')
            df['date'] = df['period'].map(str)+ '-' +df['year'].map(str)
            df['date'] = pd.to_datetime(df['date'], format='%m-%Y').apply(lambda x: x.strftime('%Y-%m'))

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
        Arguments:
            - file_name = str; Name of the file that should be outputted.
        """
        with open(f"{file_name.split('.')[0]}.json", 'w') as json_out:
            json.dump(self.raw_data, json_out, indent=4)

    def create_graph(self, title:str, graph_type:str, custom_column_names:dict=None,
            transpose:bool=False, short_location_names:bool=True, graph_labels:dict=None) -> pd.DataFrame.plot:
        """
        Returns a graph-able plotly object from the given data and constructed
        dataframe. Renames columns based on the mapping of seriesIDs to locations
        from the BLS area codes.
        Arguments:
            - title = str; graph title
            - graph_type = str;
            - custom_column_names = dict; mapping of seriesID to custom defined column names
            - transpose = bool; transpose df to graph correctly
            - short_location_names = bool; removes the state from the coumn names to shorten the length
            - graph_labels = dict; a mapping of x and y axis labels to output a graph with custom labels
        Returns a plotly express object.
        """
        #check graph type
        accepted_graphs = ['line', 'bar']
        if graph_type not in accepted_graphs:
            raise ValueError(f"Invalid graph type. Expected one of: {', '.join(accepted_graphs)}")

        #create cleaned df to use to plot data
        plotting_df = self.clean_df(custom_column_names, short_location_names)

        #transpose df, typically if length is 1
        if transpose:
            plotting_df = plotting_df.transpose()

        #bar graph
        if graph_type == 'bar':
            return px.bar(plotting_df,
                          title=title,
                          labels=graph_labels if graph_labels else {})

        #line graph
        return px.line(plotting_df,
                      labels=graph_labels if graph_labels else {},
                      title=title)

    def create_table(self, custom_column_names:dict=None,
            short_location_names:bool=True, index_color:str=None,
            descending:bool=False, index_label:str='') -> go.Figure:
        """
        Creates an html table from the dataframe with cleaned columns.
        Returns graph_object.Figure object.
        Arguments:
            - custom_column_names = dict; mapping of series ID to custom column name
            - short_location_names = bool; removes the state from the coumn names to shorten the length
            - index_color = str; the color to apply to the index column and header row.
            - descending = bool; changes indexes to sort on descending if True.
            - index_label = str; adds a custom index label to the index column in a table. Default=''
        """
        #clean dataframe
        table_df = self.clean_df(custom_column_names, short_location_names)

        #DF is sorted by ascending by default, change sort to descnding if ascending is false
        if descending:
            table_df = table_df.sort_index(ascending=False)

        #set index column color to the color passed in, set the rest to white and light gray striped
        fill_color = []
        for col in [table_df.index.name] + table_df.columns.to_list():
            if index_color and col == table_df.index.name:
                fill_color.append(index_color)
            else:
                fill_color.append(['white', 'lightgrey']*len(table_df.index))

        #Make list of all df values by column
        col_vals = [table_df[col].to_list() for col in table_df]

        #return the created table including the index
        return go.Figure(data=[go.Table(
        # header=dict(values=[index_label if index_label else table_df.index.name] + table_df.columns.to_list(),
        header=dict(values=[index_label] + table_df.columns.to_list(),
                    fill_color=index_color,
                    font=dict(color='black', size=12)),
        cells=dict(values=[table_df.index.to_list()] + col_vals,
                   fill_color = fill_color,
                   font=dict(color='black', size=11))
        )])

    def clean_df(self, custom_column_names:dict=None,
            short_location_names:bool=True) -> pd.DataFrame:
        """
        Cleans the standard dataframe up by renaming columns with locations, or applying
        the custom column names.
        Arguments:
            - custom_column_names = dict; mapping of series ID to custom column name
            - short_location_names = bool; removes the state from the coumn names to shorten the length
        """
        #create temp df to use for the table
        table_df = self.df

        #replace column names with location names
        cols = {ser_id: re.split('--|,', loc)[0] for ser_id,loc in self.locations.items()} if short_location_names else self.locations
        if custom_column_names:
            if not isinstance(custom_column_names, dict):
                raise TypeError("Custom column names must be of type dict.")
            cols.update(custom_column_names)
        table_df = table_df.rename(columns=cols, errors="raise")

        return table_df

    def _get_location(self):
        """
        Uses the area_titles.csv file from https://data.bls.gov/cew/doc/titles/area/area_titles.htm
        to create a dataframe of all area_codes that BLS uses. This returns a dict with the series
        IDs as keys and the location name as values.
        """
        series_id_locations = {}
        for series in self.series_ids:
            if re.match('EN', series[0:2]):
                area_code = re.search(r'^[A-Z]{3}([\d|U][\d|S]\d\d\d)', series).group(1)
                series_id_locations[series] = qcew_area_codes_df.loc[area_code]['area_title']
            if series[0:2] == 'LA':
                area_code = re.search(r'^[A-Z]{3}([A-Z]{2}\d{13})', series).group(1)
                series_id_locations[series] = la_area_codes_df.loc[area_code]['area_text']
            if re.match('OE', series[0:2]):
                area_code = re.search(r'^[A-Z]*(\d\d\d\d\d\d\d)', series).group(1)
                series_id_locations[series] = oes_area_codes_df.loc[area_code]['area_name']

        return series_id_locations
