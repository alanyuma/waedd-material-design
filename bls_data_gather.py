"""
bls_data_gather.py
Written by: Aaron Finocchiaro

Retrieves data from the Bureau of Labor Statistics API and formats it into Pandas Dataframes
"""
import os
import yaml
from pyBLS.BlsData import BlsData

#read in yaml file
with open('bls_config.yaml') as bls_yaml:
    bls_list = yaml.load(bls_yaml, Loader=yaml.FullLoader)

for waedd_section in bls_list:
    section_data = BlsData(
        waedd_section['seriesIDs'],
        waedd_section['start_year'],
        waedd_section['end_year'],
    )

    fig = section_data.create_graph(waedd_section['graph_name'], 
                                    graph_type=waedd_section['graph_type'],
                                    custom_column_names=waedd_section.get('custom_column_names'),
                                    transpose=waedd_section.get('transpose'),
    )
    fig.show()
    # fig.write_html(f"./graphs/{waedd_section['graph_file']}")
