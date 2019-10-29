# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Migration between Scotland and overseas by age
#
# Tabs: `AG 2001-02`, etc.

# +
from gssutils import *

if is_interactive():
    scraper = Scraper('https://www.nrscotland.gov.uk/statistics-and-data/statistics/statistics-by-theme/' \
                  'migration/migration-statistics/migration-flows/migration-between-scotland-and-overseas')
#     scraper.run()
    distribution = scraper.distribution(
        mediaType='application/vnd.ms-excel',
        title='Migration between Scotland and overseas by age')
    display(distribution)
    tabs = [tab for tab in distribution.as_databaker() if tab.name.startswith('AG ')]
    display([tab.name for tab in tabs])
    

# + {"jupyter": {"outputs_hidden": true}}
Final_table = pd.DataFrame()
# -

for tab in [t for t in tabs if t.name.startswith('AG ')]:
    flow = tab.filter('IN') | tab.filter('OUT') | tab.filter('NET')
    percentage = tab.filter('%').fill(DOWN).is_not_blank().is_not_whitespace()
    exclude = tab.filter(contains_string('Total net migration')).fill(DOWN).fill(RIGHT)
    observations = flow.fill(RIGHT).is_not_blank().is_not_whitespace() - percentage -exclude
    area = tab.filter(contains_string('Movements')).is_not_number()
    age = area.shift(0,1).expand(RIGHT).is_not_blank()
    Dimensions = [
            HDimConst('Mid Year',str(tab.name[3:7])+'-06-30T00:00:00/P1Y'),
            HDim(flow,'Flow',DIRECTLY, LEFT),
            HDim(age,'Age',DIRECTLY, ABOVE),
#             HDim(per,'per',CLOSEST, LEFT),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People'),
            HDimConst('Sex','T'),
            HDim(area,'Foreign geography',CLOSEST,ABOVE)
            ]
    c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)    
    new_table = c1.topandas()
    new_table['Flow'] = new_table['Flow'].map(
    lambda x: {
        'IN' : 'Inflow', 
        'OUT' : 'Outflow',
        'NET': 'Balance' 
        }.get(x, x))
    new_table['Age'] = new_table['Age'].map(
    lambda x: {
        '85+' : '85-plus', 
        'All ages' : 'all'        
        }.get(x, x))
    new_table['Age'] = 'nrs/' + new_table['Age']
    new_table['Mid Year'] = new_table['Mid Year'].map(lambda x: str(x)[0:4]) + '-06-30T00:00:00/P1Y'
    new_table['Domestic geography'] = 'Scotland'
    new_table = new_table[['Domestic geography','Foreign geography','Mid Year','Sex','Age','Flow','Measure Type','OBS','Unit']]
    Final_table = pd.concat([Final_table, new_table])

# + {"jupyter": {"outputs_hidden": true}}
import numpy as np
Final_table['OBS'].replace('', np.nan, inplace=True)
Final_table.dropna(subset=['OBS'], inplace=True)
if 'DATAMARKER' in Final_table.columns:
    Final_table.drop(columns=['DATAMARKER'], inplace=True)
Final_table.rename(columns={'OBS': 'Value'}, inplace=True)
Final_table['Value'] = Final_table['Value'].astype(int)

# + {"jupyter": {"outputs_hidden": true}}
Final_table['Foreign geography'] = Final_table['Foreign geography'].map(
    lambda x: {
        'Movements between Scotland and the rest of the UK1' : 'nrs/rest-of-the-uk', 
        'Movements between Scotland and overseas (including asylum seekers; excluding unmeasured migration adjustment)2, 3' : 'nrs/overseas',
        'Total net migration (including asylum seekers)3' : 'nrs/total',
        'Movements between Scotland and overseas (including asylum seekers; excluding unmeasured migration adjustment)2,3': 'nrs/overseas',
        'Movements between Scotland and Overseas (including asylum seekers)2':'nrs/overseas',
        'Total net migration (including asylum seekers)' : 'nrs/total'
        }.get(x, x))
# -

Final_table
