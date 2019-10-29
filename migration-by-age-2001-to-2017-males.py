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
# Tabs: `SYOA Persons (2001-)` and `SYOA Males (2001-)`

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
    tabs = distribution.as_databaker()
# -

Final_table = pd.DataFrame()

# +
tab = [t for t in tabs if t.name == 'SYOA Males (2001-)'][0]
cell = tab.filter('Year')
age = cell.fill(RIGHT).is_not_blank().is_not_whitespace() | cell.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace()
year = cell.shift(0,1).expand(DOWN).is_not_blank().is_not_whitespace()
flow = tab.filter(contains_string('migration')).is_not_blank().is_not_whitespace()
observations = age.fill(DOWN).is_not_blank().is_not_whitespace() 
observations = observations- cell.shift(0,1).fill(RIGHT) - year - flow

Dimensions = [
            HDim(year,'Mid Year',CLOSEST, ABOVE),
            HDim(flow,'Flow',CLOSEST, ABOVE),
            HDim(age,'Age',DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People'),
            HDimConst('Sex','M'),
            HDimConst('Domestic geography','Scotland')
    ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
new_table['Flow'] = new_table['Flow'].map(
    lambda x: {
        'In migration of males from overseas 2001-02 to latest' : 'Inflow', 
        'Out migration of males to overseas 2001-02 to latest' : 'Outflow',
        'Net migration of males from overseas 2001-02 to latest': 'Balance' 
        }.get(x, x))
new_table['Age'] = new_table['Age'].astype(str)
new_table['Age'] = new_table['Age'].map(lambda cell:cell.replace('All ages', 'all'))
new_table['Age'] = 'year/' + new_table['Age']
new_table['Age'] = new_table['Age'].map(lambda cell:cell.replace('.0', ''))
new_table.dropna(subset=['Mid Year'], inplace=True)
new_table['Mid Year'] = new_table['Mid Year'].map(lambda x: str(x)[0:4]) + '-06-30T00:00:00/P1Y'
Final_table = pd.concat([Final_table, new_table])
# -

import numpy as np
Final_table['OBS'].replace('', np.nan, inplace=True)
Final_table.dropna(subset=['OBS'], inplace=True)
if 'DATAMARKER' in Final_table.columns:
    Final_table.drop(columns=['DATAMARKER'], inplace=True)
Final_table.rename(columns={'OBS': 'Value'}, inplace=True)
Final_table['Value'] = Final_table['Value'].astype(int)

Final_table['Foreign geography'] = 'nrs/overseas'

Final_table = Final_table[['Domestic geography','Foreign geography','Mid Year','Sex','Age','Flow','Measure Type','Value','Unit']]

Final_table
