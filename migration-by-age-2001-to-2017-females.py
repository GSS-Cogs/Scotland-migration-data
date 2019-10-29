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
# Tab: `SYOA Females (2001-)`

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
    tab = distribution.as_pandas(sheet_name = 'SYOA Females (2001-)')
# -

tab

Final_table = pd.DataFrame()

observations = tab.iloc[4:21, :93]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0])
observations.columns.values[0] = -1
observations.columns.values[1] = -2
observations.drop(observations.index[0], inplace = True)
new_table = pd.melt(observations, id_vars=[-1], var_name='Age', value_name='Value')
new_table.Value.dropna(inplace =True)
new_table['temp'] = new_table[-1].str[0:2]
new_table = new_table[new_table['temp'] == '20']
new_table['Age'].fillna('anything', inplace = True)
new_table['Age'] = new_table['Age'].astype(int)
new_table['Age'] = new_table['Age'].astype(str)
new_table = new_table[new_table['Age'] != 'anything' ]
new_table.columns = ['Mid Year' if x== -1 else x for x in new_table.columns]
new_table['Unit'] = 'People'
new_table['Measure Type'] = 'Count'
new_table['Domestic geography'] = 'Scotland'
new_table['Sex'] = 'F'
new_table['Flow'] = 'Inflow'
new_table['Mid Year'] = new_table['Mid Year'].map(lambda x: str(x)[0:4])
new_table['Mid Year'] = new_table['Mid Year'] + '-06-30T00:00:00/P1Y'
new_table['Age'] = new_table['Age'].map(lambda cell: cell.replace('-2', 'all'))
new_table['Age'] = 'year/' + new_table['Age']
Final_table = pd.concat([Final_table, new_table])

observations = tab.iloc[24:41, :93]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0])
observations.columns.values[0] = -1
observations.columns.values[1] = -2
observations.drop(observations.index[0], inplace = True)
new_table = pd.melt(observations, id_vars=[-1], var_name='Age', value_name='Value')
new_table.Value.dropna(inplace =True)
new_table['temp'] = new_table[-1].str[0:2]
new_table = new_table[new_table['temp'] == '20']
new_table['Age'].fillna('anything', inplace = True)
new_table['Age'] = new_table['Age'].astype(int)
new_table['Age'] = new_table['Age'].astype(str)
new_table = new_table[new_table['Age'] != 'anything' ]
new_table.columns = ['Mid Year' if x== -1 else x for x in new_table.columns]
new_table['Unit'] = 'People'
new_table['Measure Type'] = 'Count'
new_table['Domestic geography'] = 'Scotland'
new_table['Sex'] = 'F'
new_table['Flow'] = 'Outflow'
new_table['Mid Year'] = new_table['Mid Year'].map(lambda x: str(x)[0:4])
new_table['Mid Year'] = new_table['Mid Year'] + '-06-30T00:00:00/P1Y'
new_table['Age'] = new_table['Age'].map(lambda cell: cell.replace('-2', 'all'))
new_table['Age'] = 'year/' + new_table['Age']
Final_table = pd.concat([Final_table, new_table])

observations = tab.iloc[45:62, :93]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0])
observations.columns.values[0] = -1
observations.columns.values[1] = -2
observations.drop(observations.index[0], inplace = True)
new_table = pd.melt(observations, id_vars=[-1], var_name='Age', value_name='Value')
new_table.Value.dropna(inplace =True)
new_table['temp'] = new_table[-1].str[0:2]
new_table = new_table[new_table['temp'] == '20']
new_table['Age'].fillna('anything', inplace = True)
new_table['Age'] = new_table['Age'].astype(int)
new_table['Age'] = new_table['Age'].astype(str)
new_table = new_table[new_table['Age'] != 'anything' ]
new_table.columns = ['Mid Year' if x== -1 else x for x in new_table.columns]
new_table['Unit'] = 'People'
new_table['Measure Type'] = 'Count'
new_table['Domestic geography'] = 'Scotland'
new_table['Sex'] = 'F'
new_table['Flow'] = 'Balance'
new_table['Age'] = new_table['Age'].map(lambda cell: cell.replace('-2', 'all'))
new_table['Age'] = 'year/' + new_table['Age']
new_table['Mid Year'] = new_table['Mid Year'].map(lambda x: str(x)[0:4]) + '-06-30T00:00:00/P1Y'
Final_table = pd.concat([Final_table, new_table])

Final_table['Foreign geography'] = 'nrs/overseas'

Final_table = Final_table[['Domestic geography','Foreign geography','Mid Year','Sex','Age','Flow','Measure Type','Value','Unit']]


