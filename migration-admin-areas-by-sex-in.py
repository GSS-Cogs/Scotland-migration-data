# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Migration between administrative areas and overseas by sex
#
# Tab: `In-Council Area-Sex`

# +
from gssutils import *

if is_interactive():
    scraper = Scraper('https://www.nrscotland.gov.uk/statistics-and-data/statistics/statistics-by-theme/' \
                    'migration/migration-statistics/migration-flows/migration-between-scotland-and-overseas')
#     scraper.run()
    distribution = scraper.distribution(
        mediaType='application/vnd.ms-excel',
        title='Migration between administrative areas and overseas by sex')
    display(distribution)
    tab = [tab for tab in distribution.as_databaker() if tab.name == 'In-Council Area-Sex'][0]
# -

cell = tab.filter(contains_string('Council areas'))
flow = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
midyear = cell.shift(0,2).expand(RIGHT).is_not_blank().is_not_whitespace()
observations = midyear.shift(0,1).expand(DOWN).is_not_blank().is_not_whitespace().is_not_bold() 
observations = observations.filter(lambda x: type(x.value) != str or 'Year' not in x.value) - midyear -flow
area = cell.expand(DOWN).is_not_blank().is_not_whitespace()

Dimensions = [
            HDim(midyear,'Mid Year',DIRECTLY,ABOVE),
            HDim(area,'Domestic geography', DIRECTLY, LEFT),
            HDim(flow,'flow',CLOSEST,ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People'),
            HDimConst('Flow','inflow'),
            HDimConst('Age', 'all')
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
#savepreviewhtml(c1)
tidy = c1.topandas()

tidy['Mid Year'] = tidy['Mid Year'].map(lambda x: str(x)[0:4]) + '-06-30T00:00:00/P1Y'
tidy['Foreign geography'] = 'nrs/overseas'

for col in tidy.columns:
    if col not in ['OBS']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)

tidy['Sex'] = tidy['flow'].map(lambda x: str(x)[15:])
tidy['Sex'] = tidy['Sex'].map(
    lambda x: {
        'Persons' : 'T', 
        'Females' : 'F',
        'Males': 'M' 
        }.get(x, x))

import numpy as np
tidy['OBS'].replace('', np.nan, inplace=True)
tidy.dropna(subset=['OBS'], inplace=True)
if 'DATAMARKER' in tidy.columns:
    tidy.drop(columns=['DATAMARKER'], inplace=True)
tidy.rename(columns={'OBS': 'Value'}, inplace=True)
tidy['Value'] = tidy['Value'].astype(int)

tidy = tidy[['Domestic geography','Foreign geography','Mid Year','Sex','Age','Flow','Measure Type','Value','Unit']]

tidy["source"] = "migration-admin-areas-by-sex-in"
