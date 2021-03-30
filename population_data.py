"""
Written By: Aaron Finocchiaro
3/2021

Functions to aggregate all population data for Yuma, La Paz, and Mohave Counties from azcommerce.com
for use with the WAEDD website.
"""
import os
import re
import urllib.request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

def table_color(df:pd.DataFrame, index_color:str=None) -> list:
    """
    constructs a list of colors that define the color of the plotly table.
    Arguments:
        df = pandas.DataFrame; the dataframe used to construct the table
        index_color = str; the color to use for the index column
    returns list
    """
    fill_color = []
    for col in [df.index.name] + df.columns.to_list():
        if index_color and col == df.index.name:
            fill_color.append(index_color)
        else:
            fill_color.append(['white', 'lightgrey']*len(df.index))

    return fill_color

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

    #graph data
    graphing_df = pop_df.loc[['Yuma Total', 'La Paz Total', 'Mohave Total', 'Arizona***'], [2020]]
    graphing_df = graphing_df.rename(index=lambda x: re.split(r'\*|\s(?=Total)', x)[0])
    graphing_df = graphing_df.sort_values(by=[2020], ascending=False)
    fig = px.pie(graphing_df, values=2020, names=graphing_df.index)

    #set table colors
    fill_color = table_color(graphing_df, index_color='orange')

    #create table
    table = go.Figure(data=[go.Table(
        header=dict(values=['Region', graphing_df.columns],
                    fill_color='orange',
                    align='left'),
        cells=dict(values=[graphing_df.index, graphing_df.values],
                   fill_color = fill_color,
                   align='left')
    )])
    fig.write_html("./graphs/current_population_pie.html", include_plotlyjs='cdn')
    table.write_html("./tables/current_population.html", include_plotlyjs='cdn')

def population_predictions():
    """
    Parses the excel sheet from here into a pandas dataframe:
        https://www.azcommerce.com/media/1544636/pop-prj-sumtable-medium-series2018-az.xlsx

    which shows the projected populations for each county in Arizona through 2055 and parses
    into a pandas dataFrame.
    """
    url = 'https://www.azcommerce.com/media/1544636/pop-prj-sumtable-medium-series2018-az.xlsx'
    excel_file = url.split('/')[-1]
    regions = ['Arizona', 'Yuma County',  'Mohave County', 'La Paz County']

    #download file if it doesn't exist in the waedd data dir
    if not os.path.exists(f"{WAEDD_DATA_DIR}/{excel_file}"):
        download_file(url)

    #read excel sheet and exclude certain rows from df
    population_df = pd.read_excel(f"./{WAEDD_DATA_DIR}/{excel_file}",
                                  index_col=0,
                                  skiprows=[0,1,41,42,43,44])

    #graph data 1 graph per area
    for region in regions:
        fig = px.line(population_df,
                      x=population_df.index,
                      y=region,
                      title=f'{region} Population Prediction 2018-2055')
        fig.write_html(f"./graphs/{region.lower().replace(' ','_')}_pop_predictions.html", include_plotlyjs='cdn')

    #data is indexed by date, so data needs to be organized by column in a list
    col_vals = [population_df[col].to_list() for col in population_df[regions]]

    #create table colors
    fill_color = table_color(population_df[regions], index_color='orange')

    #create table
    table = go.Figure(data=[go.Table(
        header=dict(values=['Year'] + population_df[regions].columns.to_list(),
                    fill_color='orange',
                    font=dict(color='black', size=12)),
        cells=dict(values=[population_df.index.to_list()] + col_vals,
                   fill_color = fill_color,
                   font=dict(color='black', size=11))
    )])
    table.write_html("./tables/population_predictions.html", include_plotlyjs='cdn')

if __name__ == '__main__':
    current_populations()
    population_predictions()
