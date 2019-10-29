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

# # Migration between Scotland and Overseas

from gssutils import *
scraper = Scraper('https://www.nrscotland.gov.uk/statistics-and-data/statistics/statistics-by-theme/' \
                  'migration/migration-statistics/migration-flows/migration-between-scotland-and-overseas')
scraper

scraper.dataset.theme = metadata.THEME['population']
scraper.dataset

databaker_sheets = {sheet.name: sheet for sheet in scraper.distribution(
    title='Migration between administrative areas and overseas by sex',
    mediaType=Excel).as_databaker()}

next_table = pd.DataFrame()

# +
# %%capture

tab = databaker_sheets['Net-Council Area-Sex']
# %run "migration-admin-areas-by-sex-net.ipynb"
next_table = pd.concat([next_table, tidy])

tab = databaker_sheets['In-Council Area-Sex']
# %run "migration-admin-areas-by-sex-in.ipynb"
next_table = pd.concat([next_table, tidy])

tab = databaker_sheets['Out-Council Area-Sex']
# %run "migration-admin-areas-by-sex-out.ipynb"
next_table = pd.concat([next_table, tidy])


# -

 distribution = scraper.distribution(
    title='Migration between Scotland and overseas by age',
    mediaType='application/vnd.ms-excel')
tabs = distribution.as_databaker()

# %run "migration-by-age-2001-to-2017.ipynb"
next_table = pd.concat([next_table, Final_table])

tab = distribution.as_pandas(sheet_name = 'SYOA Females (2001-)')
# %run "migration-by-age-2001-to-2017-females.ipynb"
next_table = pd.concat([next_table, Final_table])

# %run "migration-by-age-2001-to-2017-persons.ipynb"
next_table = pd.concat([next_table, Final_table])

# %run "migration-by-age-2001-to-2017-males.ipynb"
next_table = pd.concat([next_table, Final_table])

next_table.columns = ['Domestic geography1' if x=='Domestic geography' else x for x in next_table.columns]

import pandas as pd
c=pd.read_csv("scottish-geo-lookup.csv")

c

table = pd.merge(next_table, c, how = 'left', left_on = 'Domestic geography1', right_on = 'label')

table.columns = ['Domestic geography' if x=='notation' else x for x in table.columns]

table['Domestic geography'].fillna('None', inplace = True)


# +
def user_perc(x,y):
    
    if x == 'None' :
        return y
    else:
        return x
    
table['Domestic geography'] = table.apply(lambda row: user_perc(row['Domestic geography'], row['Domestic geography1']), axis = 1)

# -

table = table[['Domestic geography','Foreign geography','Mid Year','Sex','Age', 'Flow','Measure Type','Value','Unit']]

table['Value'] = table['Value'].astype(int)

table = table[table['Mid Year'] != '']

table = table[table['Mid Year'] != 'Year']

table['Age'] = table['Age'].map(
    lambda x: {
        'nrs/all' : 'all', 
        'year/all' : 'all',
        }.get(x, x))


table['Flow'] = table['Flow'].str.lower()

table['Flow'] = table['Flow'].map(
    lambda x: {
        'total' : 'resident'
        }.get(x, x))

table = table[table['Flow']  != 'resident']

from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# +
from gssutils.metadata import THEME

scraper.dataset.family = 'migration'
scraper.dataset.theme = THEME['population']
scraper.dataset.license = 'http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/'

with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
csvw = CSVWMetadata('https://gss-cogs.github.io/ref_migration/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
