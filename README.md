# waedd-material-design

Welcome to the WAEDD repository. 

Much of these are static HTML pages that do not require much regular upkeep or maintenance. This readme will mainly pertain to much of the data collection/visualization that is done inside of this repository. The following sections leverage python for data collection and visualization:

CEDS
- section 3

The purpose of including python in this website is to have an automated way to collect data. This README will cover setting up the environment to collect data as well as how to develop this further.

## Getting Started

| Requirements | Explanation |
| ------------ | ------------ |
|  Python 3.8+ | Python 3.7 might work, but has not been tested. Download the latest version from the python website  |
| Visual Studio Code | Any IDE will work, but VSCode has the most useful extensions for multiple languages |
| Git | Download from [here](https://git-scm.com/download/win) for Windows. Mac users should have this already installed |
| Live Server | VSCode extension, install this in VSCode. This is optional but recommended |
| PyLint | Linter for python, recommended for developing |
| POSTMAN | GUI API application. Not required but recommended |

Once you have verified your version of python meets the above requirements, clone this repository into your local machine. This can be done by using the "Git Bash" application on Windows or the terminal in mac. Just click the `Code` button on the main screen of the repository and copy HTTPS value and paste this into Git Bash or Terminal and use the following command:

```sh
git clone {repository URL}
```

Once complete, open VSCode to the directory that you have stored this cloned repository.

### Setup API authorization

**API KEYS ARE REQUIRED TO USE THIS.** These are mainly for the bls-data and the bea-data packages to work correctly. Follow the instructions below or go to the README for each package to get more information.
- **BLS** = Go to the [BLS Website](https://www.bls.gov/developers/home.htm) and select `registration`. Here you can signup for an API key which will allow you to make more API calls. This API key **must** be set as an environment variable. The key will be emailed to you, once you receive it, set the environment variable in your terminal as follows:

Windows:
```psh
$Env:BLS_API_KEY='{YOUR_API_KEY}'
```

Mac/Linux:
```sh
export BLS_API_KEY='{YOUR_API_KEY}'
```

- **BEA** = Go to the [BEA Website](https://apps.bea.gov/api/signup/index.cfm) and register for a key. It will be emailed to you, add it to your environment:

Windows:
```psh
$Env:BEA_API_KEY='{YOUR_API_KEY}'
```

Mac/Linux:
```sh
export BEA_API_KEY='{YOUR_API_KEY}'
```

### Python Startup

1) Create a virtual environment to work in. Virtual environments are important for managing dependancies that this project (or any project) requires. Note that the `{environment_name}` value below can be set to whatever you want.

```sh
python -m venv {environment_name}
```

2) Install required packages into python environment. This will give make sure that all of the dependancies that python doesn't come with will be installed into your environment.

```sh
pip install -r requirements.txt
```
NOTE: At this step, there may some issues with versions not working correctly. If this happens, try removing the version from the `requirements.txt` file and it should resolve this. Be careful though as this could cause strange issues with incompatible versions. It's recommended to read the release notes of these before doing this.

3) Run the scripts to make sure they are working correctly. These both should run without any errors.

```sh
python section_3.py  #Runs the script for all section 3 graphs and tables  
python section_5.py  #Runs script to get updated data for section 5
python distress.py   #Runs script for the distress page
```

### HTML Setup

Using Live Server is recommended as it will display changes in real time to HTML documents. This can be downloaded and added to Visual Studio Code by going to the extensions option on the left sidebar and searching for "Live Server". Once added, to activate it just click on the `Go Live` option on the bottom right side of the screen.

## Section 3

### Adding New Data Points from Bureau of Labor Statistics

Adding a new series from the BLS is very simple. Follow these steps:

1) Research and locate the data you need and find the series IDs. Use the [BLS Data](data.bls.gov) website and their data finder tools. All of these should provide you the series ID for what you are looking for, but it may take some work.

2) Add an entry into the bls_config.yaml and follow the format in the example below. Note that fields that don't say required are optional.

```yaml
seriesIDs:           #List of all series IDs that you need. REQUIRED
    - ENUUS00040010
    - ENU0400040010
    - ENU0401240010
    - ENU0402740010
    - ENU0401540010
  start_year: 2015  #Year that you want the data to start at. REQUIRED
  end_year: 2020    #Year that you want the data to end at. REQUIRED
  filename: 'my_test_file'  #Name used to name every outputted file. REQUIRED
  graph_name: 'Average Weekly Wages'  #Title for graph
  graph_type: 'line'  #Type of graph, options are 'line' and 'bar'. REQUIRED
  graph_mode: 'markers+lines' #Sets the plotly graph mode when updating the graph.
  graph_axis_labels:  #Sets a custom x and y axis label on the graph. 
    "date" : "Date"   #The key here should always be 'date'
    "value" : "Amount in USD"  #The key here should always be 'value'
  hovertemplate: '%{y:$.2f}'  #Custom display template for when a point is hovered over
  sort_descending: True  #Sorts values in a table in descending order instead of ascending
  transpose: False #transposes the dataframe when graphing, Default = False
  custom_column_names:  #sets custom column names in the dataframe for graphs or tables
    "ENUUS00040010" : "Region 1"
    "ENU0400040010" : "Region 2"
    "ENU0401240010" : "Region 3"
    "ENU0402740010" : "Region 4"
    "ENU0401540010" : "Region 5"
```

3) Run the script and check for errors.

4) Open the HTML files for the graph or the table produced and verify that it worked and looks how you want.


## Necessary Data

All data that is necessary for the project are located in the `waedd_data/` directory. These consist of the following documents:

- `estimates1980-2020.xlsx` = An excel spreadsheet from [AZ Commerce Population Estimates](https://www.azcommerce.com/oeo/population/population-estimates/) that has the *Current* population data for Arizona and separated by county. This will need to be updated each year when AZ Commerce publishes a new version.

- `pop-prj-sumtable-medium-series2018-az` = An excel spreadsheet from [AZ Commerce Population Projections](https://www.azcommerce.com/oeo/population/population-projections/) that has the *Predicted* population data for Arizona and separated by county for future years. This will need to be updated each year when AZ Commerce publishes a new version. This spreadsheet probably does not change very often, but it is worth checking occasionally. NOTE: This is the *"Medium Excel"* option listed in the "Summary Tables" section. 

#### HOW TO UPDATE THESE PROPERLY
If any of these spreadsheets change, chances are that the file name *will not* be the same as what `population_data.py` is set for. To download the new excel sheets:

- Go to the appropriate section of the AZ Commerce website for what you need to update.
- Find the appropriate excel sheet, right click and select `copy URL`
- Change the appropriate URL value inside of `population_data.py` script. For the population estimates (current populations) it will be the `POP_EST_EXCEL_URL` global variable. For the population predictions it will be the `POP_PREDICTION_EXCEL_URL` global variable.
- Run the script. It will notice that the desired file is missing from the `waedd_data/` directory and download it automatically.
- You may remove the old files if you no longer need them, the new file should also contain the data from the previous files.

#### If there is a problem after updating the sheets
If AZ commerce ever changes the sheets, they may also change the formatting of the sheets. The functions in `population_data.py` are designed to ignore the extra excel formatting because pandas has issues parsing it. If it is changed and there are errors when reading from the new excel sheet, follow this process:

1) Open the excel sheet with excel
2) Note which row the Excel data **starts** at (ignore any titles and other format garbage, all you want are the rows where the headers and the rows with data.)
3) Note which row the data **ends** at. Some of these sheets have footnotes and other stuff that doesn't matter for us, so ignore those lines.
4) Go into the `population_data.py` file and update the `ignore_excel_lines` list for the `population_predictions()` and the `current_populations()` functions. Note that these must be done completely and not in a range. So an example should look like this:

```python
ignore_excel_lines = [100,101,102]
```

### Further Development

Section 3 is driven by the following 2 files:

- `section_3.py` - Handles all interaction with Bureau of Labor statistics and bls-data package (Read bls-data docs for more info on this). Also handles running the functions in `population_data.py` so this one script will update all of section 3. Run this to update section 3.
- `population_data.py` - Handles all data from AZ Commerce relating to Arizona population data. There are 2 spreadsheets that are responsible for providing this data that need to be manually downloaded and updated in this repository when AZ Commerce updates them.

All graphs produced by the above functions and scripts will output graph files to `graphs/` and table files to `tables/`.

## Section 5

### Further explanation of what this is doing

The script for section 5 is filling a Jinja2 template with data and outputting an updated version of `workforce-development.html` from that data. This data all comes from the US Census Bureau and Bureu of
Labor Statistics.

The `context_dict` dictionary is very important in this script. This is a dictionary that contains all of
the data that needs to be passed to the Jinja template.

### Adding new data sources

Adding a new data source for section 5 can be done any way that the user needs to. Everything is all driven by Pandas dataframes currently, so the easiest way either modify the current `acsData` or `bls-data` objects being created, or to add new ones. Or if the user needs to, they can add a new data source that the script can interact with.

### Adding new data points

A user can either use new data points from data that is already being retrieved or they can retrive new data. Once that data is brought into the script, get it over to the jinja template by adding the new data point to  the `context_dict` dictionary.

### What to do if the script breaks?

If this script is breaking, it's probably due to one of the following issues:

- A data point was added incorrectly and the acsData class or bls-data data class is trying to do some operation on an object of `NoneType`. If this is the case, use POSTMAN or some other tool to interact with their APIs and verify the request is being made correctly.

- The BLS or Census Bureau data has changed. Sometimes these data tables change, the regions change, or something else could change on their end. Again, use POSTMAN to verify what is being returned or use their websites to verify that changes have been made and what has changed. This could impact how data needs to be displayed.

### IMPORTANT! Changing the workforce-development.html document

If **any** changes need to be made to the `workforce-development.html` document, even if they are simple changes unrelated to this script or the data in it, *THESE MUST BE MADE IN THE `workforce-development.html.jinja` FILE THAT IS IN THE `templates/` DIRECTORY.* Once the desired changes are made, run the `section_5.py` script again. 

The reason it must be done this way is because if changes are made directly to the `workforce-development.html` document, they will be overwritten the next time the `sectoin_5.py`script is run. 
