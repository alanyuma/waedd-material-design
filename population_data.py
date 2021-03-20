"""
Written By: Aaron Finocchiaro
3/2021

Functions to aggregate all population data for Yuma, La Paz, and Mohave Counties from azcommerce.com
for use with the WAEDD website.
"""
import os
import urllib.request
import pandas as pd
import plotly.express as px

WAEDD_DATA_DIR = "waedd_data"

def download_file(url:str):
    """
    Downloads excel sheet from the given url and stores it in the waedd_data directory.
    using the same file name from the url.
    """
    excel_file = url.split('/')[-1]
    print(f"Downloading {excel_file} from azcommerce.com")
    if not os.path.exists(f"{WAEDD_DATA_DIR}"):
        os.makedirs(f"{WAEDD_DATA_DIR}")
    urllib.request.urlretrieve(url, f"./waedd_data/{excel_file}")

def current_populations():
    """
    Uses the excel sheet from https://www.azcommerce.com/media/1546584/estimates1980-2020.xlsx and
    parses into Pandas dataframe.
    """
    url = 'https://www.azcommerce.com/media/1546584/estimates1980-2020.xlsx'
    excel_file = url.split('/')[-1]

    #download file if it doesn't exist in the waedd data dir
    if not os.path.exists(f"{WAEDD_DATA_DIR}/{excel_file}"):
        download_file(url)

    #parse excel sheet to pandas df, drop last col because it produces a column of NaN values
    pop_df = pd.read_excel(f"./{WAEDD_DATA_DIR}/{excel_file}",
                            sheet_name='Estimates',
                            index_col=0,
                            skiprows=[129,130,131,132])
    pop_df = pop_df.drop(pop_df.columns[42], axis=1)

    #graph data for 2020
    graphing_df = pop_df.loc[['Yuma Total', 'La Paz Total', 'Mohave Total', 'Arizona***']]
    fig = px.pie(graphing_df, values=2020, names=graphing_df.index)
    fig.write_html("./graphs/current_population_pie.html")


def population_predictions():
    """
    Parses the excel sheet from here into a pandas dataframe:
        https://www.azcommerce.com/media/1544636/pop-prj-sumtable-medium-series2018-az.xlsx

    which shows the projected populations for each county in Arizona through 2055 and parses
    into a pandas dataFrame.
    """
    url = 'https://www.azcommerce.com/media/1544636/pop-prj-sumtable-medium-series2018-az.xlsx'
    excel_file = url.split('/')[-1]

    #download file if it doesn't exist in the waedd data dir
    if not os.path.exists(f"{WAEDD_DATA_DIR}/{excel_file}"):
        download_file(url)

    #read excel sheet and exclude certain rows from df
    population_df = pd.read_excel(f"./{WAEDD_DATA_DIR}/{excel_file}",
                                  index_col=0,
                                  skiprows=[0,1,41,42,43,44])

    #graph data 1 graph per area
    for region in ['Arizona', 'Yuma County',  'Mohave County', 'La Paz County']:
        fig = px.line(population_df,
                      x=population_df.index,
                      y=region,
                      title=f'{region} Population Prediction 2018-2055')
        fig.write_html(f"./graphs/{region.lower().replace(' ','_')}_pop_predictions.html")

if __name__ == '__main__':
    current_populations()
    population_predictions()
