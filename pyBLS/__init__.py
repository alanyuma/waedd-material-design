import pandas as pd
import pkg_resources

#Construct QCEW area codes DataFrame from area code csv
qcew_stream = pkg_resources.resource_stream(__name__, 'data/area_titles.csv')
qcew_area_codes_df = pd.read_csv(qcew_stream)
qcew_area_codes_df = qcew_area_codes_df.set_index('area_fips')

#Construct OES area codes DataFrame from area code csv 
stream = pkg_resources.resource_stream(__name__, 'data/oes_areas.csv')
oes_area_codes_df = pd.read_csv(stream, converters={'area_code':lambda x: str(x)})
oes_area_codes_df = oes_area_codes_df.set_index('area_code')
