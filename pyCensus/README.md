# PyCensus

The pyCensus module is designed to interact with the United States Census Bureau API. It handles making the request to the api, and transforms the returned data into a pandas dataframe.

## Prerequisites

The following python packages must be installed into your environment:

| Package | Version |
| ------- | ------- |
| Pandas | 1.2.3+ |
| requests | 2.25.1+ |

Any versions lower than this may work, but have not been tested. 

## Setup

This tool is not yet designed to be used with an API key, but that is something that could easily be added in the future.

Beyond having the above requirements installed, there is no other setup required.

## acsData

acsData gets data from the American Community Survey API endpoint from the Census Bureau api based on certain attributes given when an object is instatiated.

Input attributes:
- `survey` = int; the name of the ACS survey (ACS 1 year, ACS 5 year, etc.)

- `year` = int; the year you are looking for.

- `group` = the ID of the table that you are looking for. To find this, visit
api.census.gov/data/{year}/acs.html and select group list).

- `geo_level_code` = int; a string value indicating the hierarchy to query with.
To find this, visit: api.census.gov/data/{year}/acs/acs{1 or 5}/geography.html.

- `for_area_codes` = list; the list of area codes to retrieve with the query. The
'for' value in the API url. For any, pass in ['*']

- `in_area_codes` = list; the list of area codes that this query is contained in.
To query for any, pass '*' for the list element(s) that need to be any.

    Default=None (This list does not need to be defined in some cases.)

- `table_type` = This could be from the following tables:
    - None (Detailed Tables),
    - subject (Subject Tables),
    - profile (Data profile),
    - cprofile (Comparison profiles).
    - Please see the documentation for the survey that you are using to
    - make sure that you have the correct format.
    - Default=None

Below is an exmaple of how acsData could be instantiated:

```python
my_acs_data = acsData(5, 2019, 'DP03', 160, ['39370', '08220', '37620'], ['04'], 'profile')
```

### acsData.clean_df

This produces a pandas dataframe from the Census Bureau data and replaces the column names with names that explain what the data point is. 

Input arguments:
    None

Returns:
    Pandas Dataframe

### acsData._get_geo_level_code

Matches geo level codes with input by making a request to the geography.html page for the requested group. Uses BeautifulSoup to scrape the geography.html page and find the correct geography type requested. Then uses this data and the other data to produce a valid url endpoint to query. Called by init.

input arguments:
- `geo_level` = int; the code corresponding to the geography type for a group, as found on the geography.html page.

- `for_areas` - list; list; the list of area codes to retrieve with the query.The 'for' value in the API url. For any, pass in ['*']

- `in_areas` = list; the list of area codes that this query is contained in. To query for any, pass '*' for the list element(s) that need to be any.

Default=None (This list does not need to be defined in some cases.)

returns str

### acsData._make_df

Construct a pandas dataframe from the raw json data from the ACS api call.

input args:
- none

returns pandas dataframe

### acsData._request_data

Requests data from the census API for the ACS endpoint.

input args:
- none

returns list
