"""
pyACS.py
Written by:Aaron Finocchiaro

A class designed to specifically work with the American Community Survey API from census.gov.
"""
# %%
import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://api.census.gov/data/"

class acsData():
    """
    Interfaces with the census.gov api for all American Community Survey data.

    Input attributes:
        - survey = int; the name of the ACS survey (ACS 1 year, ACS 5 year, etc.)

        - year = int; the year you are looking for.

        - group = the ID of the table that you are looking for. To find this, visit
        api.census.gov/data/{year}/acs.html and select group list).

        - geo_level_code = int; a string value indicating the hierarchy to query with.
        To find this, visit: api.census.gov/data/{year}/acs/acs{1 or 5}/geography.html.

        - for_area_codes = list; the list of area codes to retrieve with the query. The
        'for' value in the API url. For any, pass in ['*']

        - in_area_codes = list; the list of area codes that this query is contained in.
        To query for any, pass '*' for the list element(s) that need to be any.
        Default=None (This list does not need to be defined in some cases.)

        - table_type = This could be from the following tables:
                       None(Detailed Tables),
                       subject(Subject Tables),
                       profile(Data profile),
                       cprofile(Comparison profiles).
                       Please see the documentation for the survey that you are using to
                       make sure that you have the correct format.
                       Default=None
    """
    def __init__(self, survey:int, year:int, group:str, geo_level_code:str,
                for_area_codes:list, in_area_codes:list=None, table_type:str=None):

        table_type_options = [None, 'detailed', 'subject', 'profile', 'cprofile']

        self.survey = survey

        if survey in [1,5]:
            self.survey = survey
        else:
            raise ValueError("survey must be either 1 or 5")

        self.year = year
        self.group = group
        self.query_str = self._get_geo_level_code(geo_level_code, for_area_codes, in_area_codes)

        if table_type in table_type_options:
            if table_type == 'detailed':
                table_type = None
            self.table_type = table_type
        else:
            raise ValueError(f"table_type must match one of {table_type_options}")

        self.raw_acs_data = self._request_data()
        self.df = self._make_df()

    def _get_geo_level_code(self, geo_level:int, for_areas:list, in_areas:list) -> str:
        """
        Matches geo level codes with input by making a request to the geography.html page for the
        requested group. Uses BeautifulSoup to scrape the geography.html page and find the correct
        geography type requested. Then uses this data and the other data to produce a valid url endpoint
        to query. Called by init.

        input arguments:
            - geo_level = int; the code corresponding to the geography type for a group, as found on
            the geography.html page.
            - for_areas - list; list; the list of area codes to retrieve with the query. The
            'for' value in the API url. For any, pass in ['*']
            - in_areas = list; the list of area codes that this query is contained in.
              To query for any, pass '*' for the list element(s) that need to be any.
              Default=None (This list does not need to be defined in some cases.)

        returns str
        """
        geography_page_html = requests.get(f"{BASE_URL}{self.year}/acs/acs{self.survey}/geography.html")
        soup = BeautifulSoup(geography_page_html.text, "html.parser")
        table = soup.find('tbody')
        rows = table.find_all('tr')
        for row in rows:
            if row.find_all('td')[1].text == str(geo_level):
                geo_hierarchy = [hierarchy_level.text for hierarchy_level in row.find_all('td')[2].find_all(class_='hier')]
                break

        #construct 'for' part of query string
        query_str = f"for={geo_hierarchy.pop(-1)}:{','.join(for_areas)}"

        #construct 'in' part of query string
        if geo_hierarchy:
            if not in_areas:
                raise ValueError("in_areas value is required for this query, but none given.")
            if len(in_areas) < len(geo_hierarchy):
                raise ValueError(f"This query requires {len(geo_hierarchy)} areas for the in_areas, {len(in_areas)} given.")
            for geo_region,area_code in zip(geo_hierarchy,in_areas):
                query_str += f"&in={':'.join((geo_region,area_code))}"

        return query_str

    def _request_data(self) -> list:
        """
        Requests data from the census API for the ACS endpoint.

        input args:
            - none
        
        returns list
        """
        if '_' in self.group:
            get_param = f"get={self.group}"
        else:
            get_param = f"get=group({self.group})"

        url = f"{BASE_URL}{self.year}/acs/acs{self.survey}/{self.table_type}?{get_param},NAME&{self.query_str}"
        raw_acs_data = requests.get(url)

        return raw_acs_data.json()

    def _make_df(self) -> pd.DataFrame:
        """
        Construct a pandas dataframe from the raw json data from the ACS api call.

        input args:
            - none

        returns pandas dataframe
        """
        df = pd.DataFrame(self.raw_acs_data[1:], columns=self.raw_acs_data[0])
        df = df.loc[:,~df.columns.duplicated()]  #remove duplicate columns
        df = df.set_index('NAME')
        return df

    def clean_df(self) -> pd.DataFrame:
        """
        Replaces the column names with the actual variable names.

        Input arguments:
            - none
        
        returns pandas dataframe
        """
        variables_page_html = requests.get(f"{BASE_URL}{self.year}/acs/acs{self.survey}/profile/groups/{self.group.split('_')[0]}.html")
        soup = BeautifulSoup(variables_page_html.text, "html.parser")
        table = soup.find('tbody')
        rows = table.find_all('tr')
        name_label_dict = dict()
        for row in rows:
            row_data = row.find_all('td')
            name_label_dict[row_data[0].text] = row_data[1].text

        #replace column names
        return self.df.rename(columns=name_label_dict)
