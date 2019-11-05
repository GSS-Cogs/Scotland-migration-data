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
print(next_table.columns.values)

tab = databaker_sheets['In-Council Area-Sex']
# %run "migration-admin-areas-by-sex-in.ipynb"
next_table = pd.concat([next_table, tidy])
print(next_table.columns.values)
      
tab = databaker_sheets['Out-Council Area-Sex']
# %run "migration-admin-areas-by-sex-out.ipynb"
next_table = pd.concat([next_table, tidy])
print(next_table.columns.values)
      


# -

 distribution = scraper.distribution(
    title='Migration between Scotland and overseas by age',
    mediaType='application/vnd.ms-excel')
tabs = distribution.as_databaker()

# %run "migration-by-age-2001-to-2017.ipynb"
next_table = pd.concat([next_table, Final_table])
print(next_table.columns.values)

tab = distribution.as_pandas(sheet_name = 'SYOA Females (2001-)')
# %run "migration-by-age-2001-to-2017-females.ipynb"
next_table = pd.concat([next_table, Final_table])
print(next_table.columns.values)

# %run "migration-by-age-2001-to-2017-persons.ipynb"
next_table = pd.concat([next_table, Final_table])
print(next_table.columns.values)

# %run "migration-by-age-2001-to-2017-males.ipynb"
next_table = pd.concat([next_table, Final_table])
print(next_table.columns.values)

next_table.columns = ['Domestic geography1' if x=='Domestic geography' else x for x in next_table.columns]
print(next_table.columns.values)

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

table = table[['Domestic geography','Foreign geography','Mid Year','Sex','Age', 'Flow','Measure Type','Value','Unit', "source"]]
table[:5]

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

# -----
#
# ### TEMPORARY FIX
#
# There is a problem with this dataset where the same observation has different values depending on which source file it comes from - this is due to an inconsistent application of rounding.
#
# The data managers will investigate further, but as an interim measure, we're going to:
#
# - a) Confirm all but the early digits match where there's a duplicate (throw an exception if they don't match)
# - b) If (a) passes, use the most precise of the two values.
#

# first drop true 100% duplicated rows, they're expected and fine
# ignore the source column for this, that'll always be different - that's the point
print("Old length:", len(table))
table = table.drop_duplicates([x for x in table.columns.values if x != "source"])
print("New length:", len(table))

# +
initial_table_length = len(table)

# concatenate all dimensions except souce and Value into an "all_dimensions" column
table["all_dimensions"] = ""
for col in [x for x in list(table.columns.values) if x not in ["Value", "all_dimensions", "source"]]:
    table["all_dimensions"] += table[col]

# get value counts, use a comprehension to get duplicates only
vc = table["all_dimensions"].value_counts()
duplicated_combinations = [k for (k, v) in vc.items() if v >1]

# it's a precision difference, so we're going to:
# a) confirm the early digits
# b) take the most precise number, drop the other
for combination in duplicated_combinations:
    
    temp_df = table.copy()
    temp_df = temp_df[temp_df["all_dimensions"] == combination]
    
    if len(temp_df) != 2:
        raise ValueError("Aborting. Handling of duplicated rows has resulting in a combination that"
                        "is not appearing exactly twice....something unexpected has occurred. For "
                         "dimension combination {}.".format(combination))
    
    # Compare precision of the last two digits    
    both_values = list(temp_df["Value"].unique())
    
    # First we need to make sure we're picking between comprable numbers
    # Comparing the earlier digits is a bit tricky as the precision varies depending
    # on the size of the number (i.e you dont round 200 to closest 5 digit figure)
    # The pattern seems to be 2 digits rounding for 3 figures, and 3 digit rounding for higher
    if both_values[0] < 1000 and both_values[1] < 1000:
        compare_without_last = 2
    else:
        compare_without_last = 3
    
    if str(both_values[0])[:-compare_without_last] != str(both_values[1])[:-compare_without_last]:
        
        # Anything less than 100 gets rounded to 100.....
        if 100 in both_values and both_values[0] < 100 or both_values[1] < 100:
            pass # it's fine
        else:
            raise ValueError("Aborting. We have duplicate numbers that appear to be differentiated by "
                        "more than just rounding off, these: {}".format(",".join([str(x) for x in both_values])))
        
    # Now we compare precision and drop the least precise
    both_values = list(temp_df["Value"].unique())
    
    decided = False
    # Consider the last two digits
    for i in [-1, -2]:

        # if we've rounded the first number take the second
        if str(both_values[0])[i] == "0" and str(both_values[1])[i] != "0":
            chosen_value = both_values[1]
            decided = True
            break

        # if we've round the second, take the first
        elif str(both_values[1])[i] == "0" and str(both_values[0])[i] != "0":
            chosen_value = both_values[0]
            decided = True
            break
            
    if not decided:
        # If the difference isn't obvious to our current logic, we need to blow up
        raise ValueError("Aborting, unable to ascertain which value has been rounded from {}." \
                        .format(",".join([str(x) for x in both_values])))
        
    print(chosen_value, "from", both_values)
    index_to_drop = table[(table["all_dimensions"] == combination) & (table["Value"] != chosen_value)].index.tolist()
    table = table.drop(index=index_to_drop[0])

# Sanity check, make sure we've lost exactly one row for each duplication found
if (initial_table_length - len(duplicated_combinations)) != len(table):
    raise ValueError("Aborting. Handling for the duplication issue has resulted in a table of"
                    "unexpected length. Expected '{}', got '{}'.".format(len(duplicated_combinations),
                     len(table)))
    


# +
# One last sanity check to make sure all duplications have been removed
vc = table["all_dimensions"].value_counts()
duplicated_combination_final_check = [k for (k, v) in vc.items() if v >1]
if len(duplicated_combination_final_check) != 0:
    raise ValueError("Aborting. We have more than one value for a given dimension combination.")
    
# tidy up
table = table.drop("all_dimensions", axis=1)
# -

# end of temporary fix
#
# -----

# We're gonna drop "source" dimension here but I'm leaving it in the earlier recipe
# if we get any more duplication issues it's a good way to untangle them
table = table.drop("source", axis=1)

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
