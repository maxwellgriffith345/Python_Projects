# This script is used to to extract NPVRR component data from the selected model(s).
# Import the following packages shown below.
import os, sys, clr
import pandas as pd
import glob

# Plexos code, current version doesn't need to be updated to run later upgrades.
sys.path.append('C:/Program Files/Energy Exemplar/PLEXOS 8.3')
clr.AddReference('PLEXOS7_NET.Core')
clr.AddReference('EEUTILITY')

from PLEXOS7_NET.Core import *
from EEUTILITY.Enums import *

# Enter the locations for the solution files you want to reference.
# The text should appear green with quotes ('') on each side if you entered it correctly.
print("Getting solution names from folder.")
# Location = 'Z:\IRP 2023\PLEXOS Solutions for PBI - KSC 9ep'
Location = 'Z:/IRP 2023/DRs/KCC - Justin backup/9ep Solutions'

# Use lines 23 and 24 if you want every model/solution in the aforementioned folder
# Use line 25 if you only want specific model(s)/solution(s)
Solution_list = os.listdir(Location)
Solution_list = [sub.replace(' Solution.zip', '') for sub in Solution_list]
# Solution_list = ['Model EVG M3C FEBBVAA']

print("Solutions acquired.")

# Wait for the script to finish running before opening the file, as the script will stop running if the file is open and generate an error when it tries to retrieve or edit the data in the file.

#**********DO NOT GO PAST THIS POINT UNLESS YOU ARE EDITING THE SCRIPT.**********

# This section removes the temporary data from the prior run.
print('Removing previous model data.')

for folder, subfolders, files in os.walk('Z:/Python/Temp data/NPVRR Rankings'):
    for file in files:
        if file.endswith('.csv'):
            path = os.path.join(folder, file)
            print('deleted: ', path)
            os.remove(path)

print('Removal complete.  Now writing new data.')

# This section begins the data loop to generate the temporary files by looking up the solution files based on the location and model(s) provided.
for x in Solution_list:
    print(x)
    try:
        sol = Solution()
        sol_file = '' + Location + '/' + x + ' Solution.zip'

        sol.Connection(sol_file)

        print('Pulling Cost to Load data.')

        results = sol.QueryToCSV('Z:/Python/Temp data/NPVRR Rankings/'+x+' Cost to Load data.csv', False, SimulationPhaseEnum.LTPlan, \
            CollectionEnum.SystemRegions, \
            '', \
            '', \
            PeriodEnum.FiscalYear, \
            SeriesTypeEnum.Values, \
            '66')

        print('Pulling Generator Pool Revenue data.')

        results = sol.QueryToCSV('Z:/Python/Temp data/NPVRR Rankings/'+x+' Generator Pool Revenue data.csv', False, SimulationPhaseEnum.LTPlan, \
            CollectionEnum.SystemRegions, \
            '', \
            '', \
            PeriodEnum.FiscalYear, \
            SeriesTypeEnum.Values, \
            '67')

        print('Pulling Total Cost data.')

        results = sol.QueryToCSV('Z:/Python/Temp data/NPVRR Rankings/'+x+' Total Cost data.csv', False, SimulationPhaseEnum.LTPlan, \
            CollectionEnum.SystemRegions, \
            '', \
            '', \
            PeriodEnum.FiscalYear, \
            SeriesTypeEnum.Values, \
            '167')

        print('Pulling Retirement Cost data.')

        results = sol.QueryToCSV('Z:/Python/Temp data/NPVRR Rankings/'+x+' Retirement Cost data.csv', False, SimulationPhaseEnum.LTPlan, \
            CollectionEnum.SystemRegions, \
            '', \
            '', \
            PeriodEnum.FiscalYear, \
            SeriesTypeEnum.Values, \
            '163')

        print('Pulling Penalty Cost data.')

        results = sol.QueryToCSV('Z:/Python/Temp data/NPVRR Rankings/'+x+' Penalty Cost data.csv', False, SimulationPhaseEnum.LTPlan, \
            CollectionEnum.SystemConstraints, \
            '', \
            '', \
            PeriodEnum.FiscalYear, \
            SeriesTypeEnum.Values, \
            '8')
    except:
        pass

# This section combines all the temporary data files created above into one excel file.
print('Aggregating data.')
os.chdir(('Z:/Python/Temp data/NPVRR Rankings'))
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
combined_df = pd.concat([pd.read_csv(f) for f in all_filenames])

# combined_df.shape

# This section is removing all unnecessary data, including extra columns, properties, and other data.
print('Formatting and generating data file.')
combined_df.drop(
    columns=['parent_class_id', 'parent_id', 'property_id', 'band_id', 'unit_id', 'parent_name', 'collection_id', 'category_id', 'category_rank', 'child_id', 'timeslice_name', 'sample_name', 'interval_id', 'phase_id', 'phase_name','collection_name'], inplace=True)

# This section reformats the file into the correct layout by making new columns, renaming old ones, and choosing what columns to publish to the final excel file.
combined_df[['Utility', 'Endpoint Name', 'Plan Name']] = combined_df['model_name'].str.split(' ', n=2, expand=True)

# combined_df = combined_df[combined_df['category_name'].isin(['Zonal Regions', 'Markets', 'NG Conversions'])]

combined_df.rename(columns={'child_name': 'Unit or Zonal Region'}, inplace=True)
combined_df.rename(columns={'property_name': 'Property'}, inplace=True)
combined_df.rename(columns={'_date': 'Date'}, inplace=True)
#combined_df.rename(columns={'unit_name': 'Value Type'}, inplace=True)
combined_df.rename(columns={'value': 'Value ($000)'}, inplace=True)
#combined_df.rename(columns={'collection_name': 'Class Type'}, inplace=True)
combined_df.rename(columns={'category_name': 'Category'}, inplace=True)
combined_df.rename(columns={'model_name': 'Model Name'}, inplace=True)
combined_df.rename(columns={'period_id': 'Period'}, inplace=True)

# This section reformats the file to be set up to pull data using Power BI/Excel.
combined_df = combined_df[['Utility', 'Plan Name', 'Endpoint Name', 'Category', 'Unit or Zonal Region', 'Property', 'Value ($000)', 'Date', 'Period']]
# combined_df = combined_df[['Utility', 'Endpoint Name', 'Plan Name', 'Model Name', 'Category', 'Unit or Zonal Region', 'Property', 'Value ($000)', 'Date', 'Period']]

df_pivot = combined_df.pivot(index=['Utility', 'Plan Name', 'Endpoint Name', 'Category', 'Unit or Zonal Region', 'Date', 'Period'], columns='Property', values=['Value ($000)'])
# df_pivot = combined_df.pivot(index=['Utility', 'Endpoint Name', 'Plan Name', 'Model Name', 'Category', 'Unit or Zonal Region', 'Date', 'Period'], columns='Property', values=['Value ($000)'])

df_pivot.columns = df_pivot.columns.droplevel()

# print(df_pivot)

modified_df = df_pivot.rename_axis(None, axis=1)

# print(modified_df)

modified_df = modified_df.reset_index()

# print(modified_df)

modified_df.rename(columns={'Cost to Load': 'Cost to Load ($000)'}, inplace=True)
modified_df.rename(columns={'Generator Pool Revenue': 'Generator Pool Revenue ($000)'}, inplace=True)
modified_df.rename(columns={'Total Cost': 'Total Cost ($000)'}, inplace=True)
modified_df.rename(columns={'Generator Retirement Cost': 'Retirement Cost ($000)'}, inplace=True)
modified_df.rename(columns={'Penalty Cost': 'Penalty Cost ($000)'}, inplace=True)

modified_df = modified_df[['Utility', 'Plan Name', 'Endpoint Name', 'Category', 'Unit or Zonal Region', 'Cost to Load ($000)', 'Generator Pool Revenue ($000)', 'Total Cost ($000)', 'Retirement Cost ($000)', 'Penalty Cost ($000)', 'Date', 'Period']]
# modified_df = modified_df[['Utility', 'Endpoint Name', 'Plan Name', 'Model Name', 'Category', 'Unit or Zonal Region', 'Cost to Load ($000)', 'Generator Pool Revenue ($000)', 'Total Cost ($000)', 'Retirement Cost ($000)', 'Penalty Cost ($000)', 'Date', 'Period']]

# This section is used to generate the file at its correct location.
# modified_df.to_excel('Z:/IRP 2023/Plan Workbooks/NPVRR Rankings Data/New EVG NPVRR Data.xlsx', sheet_name='Data', index=False, encoding='utf-8-sig')
# modified_df.to_excel('Z:/IRP 2023/Plan Workbooks/NPVRR Rankings Data/New KSC NPVRR Data.xlsx', sheet_name='Data', index=False, encoding='utf-8-sig')
# modified_df.to_excel('Z:/IRP 2023/Plan Workbooks/NPVRR Rankings Data/New MET NPVRR Data.xlsx', sheet_name='Data', index=False, encoding='utf-8-sig')
# modified_df.to_excel('Z:/IRP 2023/Plan Workbooks/NPVRR Rankings Data/New MOW NPVRR Data.xlsx', sheet_name='Data', index=False, encoding='utf-8-sig')

modified_df.to_excel('Z:/IRP 2023/DRs/KCC - Justin backup/NPVRR Data/KCC NPVRR Data.xlsx', sheet_name='Data', index=False)

print('NPVRR Rankings Data input file created.')
