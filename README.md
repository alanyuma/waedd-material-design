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

**API KEYS ARE REQUIRED TO USE THIS.** There is more on this in the pybls module docs. However, the easiest way to do this is to go to the [BLS Website](https://www.bls.gov/developers/home.htm) and select `registration`. Here you can signup for an API key which will allow you to make more API calls. This API key **must** be set as an environment variable. The key will be emailed to you, once you receive it, set the environment variable in your terminal as follows:

Windows:
```psh
$Env:BLS_API_KEY='{YOUR_API_KEY}'
```

Mac/Linux:
```sh
export BLS_API_KEY='{YOUR_API_KEY}'
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
python bls_data_gather.py
python population_data.py
```

### HTML Setup

Using Live Server is recommended as it will display changes in real time to HTML documents. This can be downloaded and added to Visual Studio Code by going to the extensions option on the left sidebar and searching for "Live Server". Once added, to activate it just click on the `Go Live` option on the bottom right side of the screen.

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
If AZ commerce ever changes the sheets, they may also change the formatting of the sheets. The `population_data.py` script is designed to ignore the extra excel formatting because pandas has issues parsing it. If it is changed and there are errors when reading from the new excel sheet, follow this process:

1) Open the excel sheet with excel
2) Note which row the Excel data **starts** at (ignore any titles and other format garbage, all you want are the rows where the headers and the rows with data.)
3) Note which row the data **ends** at. Some of these sheets have footnotes and other stuff that doesn't matter for us, so ignore those lines.
4) Go into the `population_data.py` file and update the `ignore_excel_lines` list for the `population_predictions()` and the `current_populations()` functions. Note that these must be done completely and not in a range. So an example should look like this:

```python
ignore_excel_lines = [100,101,102]
```

### Further Development

Section 3 is driven by the following 2 scripts:

- `bls_data_gather.py` - Handles all interaction with Bureau of Labor statistics and pybls package. Read pybls docs for more info on this
- `population_data.py` - Handles all data from AZ Commerce relating to Arizona population data. There are 2 spreadsheets that are responsible for providing this data that need to be manually downloaded and updated in this repository when AZ Commerce updates them.

These scripts are run individually and update the graphs in the `graphs/` directory and the tables in the `tables/` directories automatically. 

