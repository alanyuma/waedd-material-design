"""
section_4.py
Written by: Aaron Finocchiaro

Gathers data for section 5 from the US Census Bureau and the Bureau of Labor Statistics
and fills a Jinja template to update the HTML document.

Usage:
    python section_5.py

Adding more data:
    - To add a new source (so a new place where data needs to be requested from), add it 
      to the data request section.
    - To add a new data point to the context_dict to be referenced in the jinja template,
      just add a section to this script to pull that data out from the dataframe and add
      it to the context_dict. Be sure to follow the sections and formatting to keep it easy
      to follow.
"""
import calendar
import datetime
import locale
import pandas as pd
from jinja2 import FileSystemLoader, Environment
from pybls.bls_data import BlsData
from pyCensus.pyAcs import acsData

#constants
locale.setlocale(locale.LC_ALL, '')
area_dict = {
    'Kingman city, Arizona' : 2133,
    'Lake Havasu City city, Arizona' : 2396,
    'Bullhead City city, Arizona' : 2591,
    'Yuma County, Arizona': 5519,
    'La Paz County, Arizona': 4514
}
context_dict = dict()

def comma_separated(number:int) -> str:
    """
    Custom Jinja filter to format numbers to be separated by commas.
    Args:
        - number; int passed from jinja template
    returns str
    """
    return f"{number:n}"

#####
#### Data Requests ####
#####

#request Census Bureau data
acs_econ_data = acsData(5, 2019, 'DP03', 160, ['39370', '08220', '37620'], ['04'], 'profile')
county_econ_data = acsData(5, 2019, 'DP03', '050', ['027', '012'], ['04'], 'profile')
population_data = acsData(5, 2019, 'DP05_0001E', 160, ['39370', '08220', '37620'], ['04'], 'profile')
county_pop_data = acsData(5, 2019, 'DP05_0001E', '050', ['027', '012'], ['04'], 'profile')

#request BLS Data
bls_employment_data = BlsData(
    ['LAUCT043937000000003','LAUCT043762000000003', 'LAUCT040822000000003', 'LAUCN040120000000003', 'LAUCN040270000000003', 'LASST040000000000003'],
    datetime.datetime.today().date().year - 10,
    datetime.datetime.today().date().year
)

#create a cleaned df for each to work with. Also append county dataframes to regular city/town data for dataframes from census
clean_acs_df = acs_econ_data.clean_df().append(county_econ_data.clean_df())
clean_county_acs_df = county_econ_data.clean_df()
clean_pop_df = population_data.clean_df().append(county_pop_data.clean_df())
clean_bls_employment_df = bls_employment_data.clean_df()

#add ACS survey year to context (mainly to show what year the data is pertenant to)
context_dict['acs_year'] = acs_econ_data.year

#####
#### Employment and Unemployment ####
#####

#current emplyment data from Census
context_dict['employment'] = dict(clean_acs_df['Estimate!!EMPLOYMENT STATUS!!Population 16 years and over!!In labor force!!Civilian labor force!!Employed'])

#iterate bls dataframe columns to get specific Unemployment datapoints
for col in clean_bls_employment_df:

    #Get current unemplyoment data. Adds a list of [month-year, unemployment_percentage] to context data.
    current_valid = clean_bls_employment_df[col].last_valid_index()
    context_dict[f"current_unemployment:{col}"] = [
        f"{calendar.month_name[int(current_valid.split('-')[1])]} {current_valid.split('-')[0]}",
        clean_bls_employment_df[col][current_valid]
    ]

    #Find point in time with highest unemployment data. Adds a list of [month-year, unemployment_percentage] to context data.
    max_idx = clean_bls_employment_df[col].idxmax()
    context_dict[f"max_unemployment:{col}"] = [
        f"{calendar.month_name[int(max_idx.split('-')[1])]} {max_idx.split('-')[0]}",
        clean_bls_employment_df[col][max_idx]
    ]

    #Difference between current unemployment for a region and the whole state of AZ. Adds a list of [unemployment_percentage, (higher|lower)]
    #to context data.
    state_diff = round(clean_bls_employment_df[col][current_valid] - clean_bls_employment_df['Arizona'][current_valid],2)
    context_dict[f"current_unemployment_vs_AZ:{col}"] = [abs(state_diff), f"{'higher' if state_diff > 0 else 'lower'}"]

    #Difference between peak unemployment and current. Adds a list of [unemployment_percentage, (higher|lower)]
    #to context data.
    peak_diff = round(clean_bls_employment_df[col][current_valid] - clean_bls_employment_df[col][max_idx],2)
    context_dict[f"current_unemployment_vs_peak:{col}"] = [abs(peak_diff), f"{'higher' if peak_diff > 0 else 'lower'}"]

#Per-industry employment data. Make a df of just the industry percents, then iterate the cols and locate the
#top 3 percentages for each region. Add these to the context_dict with the industry names.
industry_df = clean_acs_df.filter(regex=r'^Percent!!INDUSTRY!!Civilian employed population 16 years and over!!.*')
industry_df = industry_df.rename(lambda x: x[len('Percent!!INDUSTRY!!Civilian employed population 16 years and over!!'):], axis=1)
industry_df = industry_df.apply(pd.to_numeric)
industry_df = industry_df.transpose()

for col in industry_df.columns:
    top_3 = industry_df[col].nlargest(3)
    context_dict[f"top-industries:{col}"] = dict(top_3)


#####
#### Income data ####
#####

#Per capita income
context_dict['per_capita_income'] = dict(clean_acs_df['Estimate!!INCOME AND BENEFITS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!Per capita income (dollars)'])

#Households making between $15k and $50k per year for each region
pct_income_benefits = 'Percent!!INCOME AND BENEFITS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!'
context_dict['pct_hh_between_15_50'] = dict(round(
    pd.to_numeric(clean_acs_df[f"{pct_income_benefits}Total households!!$15,000 to $24,999"]) +
    pd.to_numeric(clean_acs_df[f"{pct_income_benefits}Total households!!$25,000 to $34,999"]) +
    pd.to_numeric(clean_acs_df[f"{pct_income_benefits}Total households!!$35,000 to $49,999"]),2))

#####
#### Population and household data ####
#####

#total households
total_households_df = clean_acs_df["Estimate!!INCOME AND BENEFITS (IN 2019 INFLATION-ADJUSTED DOLLARS)!!Total households"]
context_dict['total_households'] = dict(total_households_df)

#City Population
context_dict['population'] = dict(clean_pop_df['Estimate!!SEX AND AGE!!Total population'])

#population density
for region,area in area_dict.items():
    density = round(pd.to_numeric(clean_pop_df['Estimate!!SEX AND AGE!!Total population'].loc[region]) / area,2)
    context_dict[f"pop_density:{region}"] = density

#avg household size
context_dict['avg_hh_size'] = dict(
    round(pd.to_numeric(clean_pop_df['Estimate!!SEX AND AGE!!Total population']) / pd.to_numeric(total_households_df),2)
)

#Poverty rate in last 12 months
context_dict['poverty_rate'] = dict(
    clean_acs_df["Percent!!PERCENTAGE OF FAMILIES AND PEOPLE WHOSE INCOME IN THE PAST 12 MONTHS IS BELOW THE POVERTY LEVEL!!All people"]
)

#prepare Jinja template
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
env.filters['comma_separated'] = comma_separated
template = env.get_template("workforce-development.html.jinja")

#open file and output a rendered jinja template
with open("workforce-development.html", 'w', encoding='utf-8') as output_html:
    output_html.write(template.render(context_dict=context_dict))
