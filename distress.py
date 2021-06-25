"""
A script designed to update and display the Distress page data for waedd.org/distress

By: Aaron Finocchiaro
"""
import datetime
import re
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from pyBea.bea_data import regionalData
from pybls.bls_data import BlsData
from pyCensus.acsData import acsData

def distress_table_fill_colors(df:pd.DataFrame) -> list:
    """
    Takes a dataframe and determines the fill colors for the table that is going to be
    created from the dataframe. It will color the column headers and the index column orange,
    use white and light grey stripes for the regular columns, and highlight cells that are beyond
    the threshold limit in the threshold column yellow.
    """
    fill_color = ['orange']
    for col in df.columns:
        if col == "Threshold":
            threshold_color = ['white'] #unemployment cell, will always be white
            for val in list(df["Threshold"])[1:]:
                if val < .8:
                    threshold_color.append('yellow')
                elif val % 2 == 0:
                    threshold_color.append('lightgrey')
                elif val % 2 != 0:
                    threshold_color.append('white')
            fill_color.append(threshold_color)
        else:
            fill_color.append(['white', 'lightgrey']*len(df.index))
    return fill_color

def distress_table(df:pd.DataFrame) -> go.Figure:
    """
    Takes a pandas dataframe and constructs a plotly graph objects table based on
    the dataframe.
    """
    #determine the fill colors
    fill_colors = distress_table_fill_colors(df)

    #apply units ($ and %) to the appropriate data
    df['Threshold'] = df['Threshold'].apply('{}%'.format)
    df.iloc[0, df.columns != 'Threshold'] = df.iloc[0, df.columns != 'Threshold'].apply('{}%'.format)
    df.loc['2019 Per Capita Money Income (5-year ACS)':, df.columns != 'Threshold'] = (
        df.loc['2019 Per Capita Money Income (5-year ACS)':, df.columns != 'Threshold'].applymap('${:,.2f}'.format)
    )

    #create table
    col_vals = [df[col].to_list() for col in df]
    return go.Figure(data=[go.Table(
        header=dict(values=["Criteria"] + df.columns.to_list(),
                    line_color="black",
                    fill_color="orange",
                    font=dict(color='black', size=12)),
        cells=dict(values=[df.index.to_list()] + col_vals,
                   line_color="black",
                   fill_color=fill_colors)
    )])

def make_df(data:dict) -> pd.DataFrame:
    """
    Makes a dataframe based on a dict of values passed in and creates the threshold column for that
    data.
    Arguments:
        - data = dict; data to be added to dataframe
    Returns dataframe
    """
    df = pd.DataFrame(
            data,
            index=["24-month Average Unemployment Rate (BLS)",
                    "2019 Per Capita Money Income (5-year ACS)",
                    "2019 Per Capita Personal Income (BEA)"],
        )
    df = df.apply(pd.to_numeric)
    df['Threshold'] = round(df.iloc[:,0]/df['United States'], 2)
    return df

if __name__ == '__main__':
    #gather BLS data for the past 3 years from most recent available month
    bls_unemployment = BlsData(
        ["LAUST040000000000003", "LAUCN040120000000003", "LAUCN040270000000003", "LAUCN040150000000003", "LNU04000000"],
        (datetime.date.today() - relativedelta(years=3)).year,
        datetime.date.today().year,
    )
    bls_unemployment_df = bls_unemployment.clean_df(custom_column_names={"LNU04000000": "United States"})

    # remove NaN entries for lines with national data and not state data (usually most recent month)
    bls_unemployment_df = bls_unemployment_df.dropna()

    # remove entries outside of 24 previous months
    bls_unemployment_df = (
        bls_unemployment_df[~(
            pd.to_datetime(bls_unemployment_df.index) < pd.to_datetime(bls_unemployment_df.iloc[-1].name) -
            pd.DateOffset(months=24))]
    )

    # gather Census ACS data
    county_data = acsData(5, 2019, 'DP03_0088E', '050', ['012', '015', '027'], ['04'], 'profile').df.transpose()
    state_data = acsData(5, 2019, 'DP03_0088E', '040', ['04'], table_type='profile').df.transpose()
    national_data = acsData(5, 2019, 'DP03_0088E', '010', ['1'], table_type='profile').df.transpose()
    census_data = pd.concat([county_data, state_data, national_data], axis=1)
    census_data = census_data.rename(columns=lambda x: re.sub(',.*', '', x))

    #gather BEA data
    bea_data = regionalData("CAINC1", 3, ["04015", "04027", "04012", "04000", "00000"], ["2019"]).df
    bea_data = bea_data.rename(columns=lambda x: re.sub(',.*', ' County', x))
    bea_data.iloc[0] = bea_data.replace(',','',regex=True)

    #make graph
    bls_graph = bls_unemployment.create_graph('24 month Unemployment Data (BLS)',
                                   graph_type='line',
                                   graph_labels={"date":"Date", "value": "Percent Unemployed"},
                                   custom_column_names={"LNU04000000": "United States"})
    bls_graph.update_traces(mode='markers+lines', hovertemplate='%{y}%')
    bls_graph.update_layout(hovermode='x')
    bls_graph.write_html("./graphs/region_distress_unemployment.html", include_plotlyjs='cdn')

    #make a dataframe from the combined averages for all counties in the region
    combined_data = {
        'Region' : [round(bls_unemployment_df[['La Paz County', 'Mohave County', 'Yuma County']].mean().mean(), 2),
                    round(census_data.loc[:'DP03_0088E', 'Yuma County':'Mohave County'].mean().mean(), 2),
                    round(bea_data[['La Paz County', 'Mohave County', 'Yuma County']].mean().mean(), 2)],
        'Arizona' : [round(bls_unemployment_df['Arizona'].mean(), 2), census_data.loc['DP03_0088E']['Arizona'], bea_data['Arizona'][0]],
        'United States' : [round(bls_unemployment_df['United States'].mean(), 2),
                            census_data.loc['DP03_0088E']['United States'],
                            bea_data['United States'][0]],
    }
    combined_region_df = make_df(combined_data)

    #make the region distress table from the dataframe and write to html doc
    combined_table = distress_table(combined_region_df)
    combined_table.write_html("./tables/region_combined_distress.html", include_plotlyjs='cdn')

    # make county-based tables
    for region in ['La Paz County', 'Mohave County', 'Yuma County']:

        # gather data
        county_data = {
            region : [round(bls_unemployment_df[region].mean(), 2), census_data.loc['DP03_0088E'][region], bea_data[region][0]],
            'Arizona' : [round(bls_unemployment_df['Arizona'].mean(), 2), census_data.loc['DP03_0088E']['Arizona'], bea_data['Arizona'][0]],
            'United States' : [round(bls_unemployment_df['United States'].mean(), 2),
                                census_data.loc['DP03_0088E']['United States'],
                                bea_data['United States'][0]],
        }

        #create new df for data
        county_df = make_df(county_data)

        #create table and write to html doc
        table = distress_table(county_df)
        table.write_html(f"./tables/{'_'.join(region.lower().split()[:-1])}_distress.html", include_plotlyjs='cdn')
