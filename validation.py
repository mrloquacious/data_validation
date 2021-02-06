import pandas as pd
import numpy as np
from pandas_schema import Column, Schema
from pandas_schema.validation import CustomElementValidation, InRangeValidation, IsDistinctValidation 
import os

path = os.path.abspath('.')
datafile = path + "/Oregon_Hwy_26_Crash_Data_for_2019.csv"  

df = pd.read_csv(datafile)

null_validation = CustomElementValidation(lambda d: d is not np.nan, 'this field cannot be null')

# This was my first try. It's better to separate into 3 dataframes as I did later.
# Serial # returns some duplicates, but is a bit squirrely, so I've abandoned for now.

# Use pandas_schema library to organize which parameters to use to validated each column:
schema = Schema([
            Column('Crash ID', [null_validation, InRangeValidation(00000000, 100000000)]),
            Column('Serial #', [InRangeValidation(1, 100000), IsDistinctValidation()], allow_empty=True), 
            Column('Crash Day', [InRangeValidation(1,32)], allow_empty=True)
            ])

'''
# Print the violations:
errors = schema.validate(df.loc[:,['Crash ID', 'Serial #', 'Crash Day']])
for error in errors:
    print(error)
'''

# Narrow the validation to crash records only:  
schema_crash = Schema([
            # Verify for crash records that every record has a unique non-null ID:
            Column('Crash ID', [null_validation, IsDistinctValidation()]),
            Column('Serial #', [null_validation, InRangeValidation(1, 100000)]),
            Column('Crash Day', [null_validation, InRangeValidation(1,32)]),
            Column('Crash Month', [null_validation, InRangeValidation(1,13)]),
            Column('Crash Year', [null_validation, InRangeValidation(2019)]),
            Column('Total Vehicle Count', [null_validation]),
            # This is causing trouble because I think the data is being treated as a string, not int:
            Column('Alcohol-Involved Flag', [InRangeValidation(0,1.0)]),
            ])

# Create a separate dataframe for each of the 3 types of records: 
# Crash, Vehicle, and Participant. Then drop unnecessary columns. 
df_crash = df[df['Record Type'] == 1]
df_crash = df_crash.dropna(axis=1, how='all')
df_vehicle = df[df['Record Type'] == 2]
df_vehicle = df_vehicle.dropna(axis=1, how='all')
df_participant = df[df['Record Type'] == 3]
df_participant = df_participant.dropna(axis=1, how='all')

# Print violations 
errors_crash = schema_crash.validate(df_crash.loc[:,['Crash ID', 'Serial #', 'Crash Day', 'Crash Month', 'Crash Year', 'Total Vehicle Count', 'Alcohol-Involved Flag']])
for error in errors_crash:
    print(error)
