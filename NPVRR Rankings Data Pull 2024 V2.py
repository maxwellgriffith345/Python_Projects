# This script is used to to extract NPVRR component data from the selected model(s).
# Import the following packages shown below.
import os, sys, clr
import pandas as pd
import glob
from openpyxl import load_workbook
import pathlib
import xlwings as xw
import shutil
from System import DateTime, String
import numpy as np
from datetime import datetime, timedelta

#Plexos code, current version doesn't need to be updated to run later upgrades.
sys.path.append(r'C:\Program Files\Energy Exemplar\PLEXOS 9.0 API')
clr.AddReference('PLEXOS_NET.Core')
clr.AddReference('EEUTILITY')
clr.AddReference('EnergyExemplar.PLEXOS.Utility')

from PLEXOS_NET.Core import *
from EEUTILITY.Enums import *
from EnergyExemplar.PLEXOS.Utility.Enums import *

def getdf(sol, columns, types,collection, properties=''):
    results_listyear = sol.QueryToList(
        SimulationPhaseEnum.LTPlan, \
        collection, \
        '', \
        '', \
        PeriodEnum.FiscalYear, \
        SeriesTypeEnum.Values, \
        properties)
    df = pd.DataFrame([[row.GetProperty.Overloads[String](n) for n in columns] for row in results_listyear],
                      columns=columns)
    # clean up data types
    df = df.astype(types)
    df['_date']=pd.to_datetime(df['_date'], format='%m/%d/%Y %I:%M:%S %p')
    return df

columns = ['child_name', 'property_name', '_date','value', 'category_name', 'model_name', 'period_id']

column_names={'child_name': 'Unit or Zonal Region','property_name': 'Property', '_date': 'Date',
              'value': 'Value ($000)', 'category_name': 'Category', 'model_name': 'Model Name', 'period_id': 'Period'}

types = {'child_name': "string",'property_name': "string", 'model_name': "string",
           'category_name': "string", 'value': np.float32, '_date': "string"}

# Enter the locations for the solution files you want to reference.
# The text should appear green with quotes ('') on each side if you entered it correctly.
print("Getting solution names from folder.")
# Location = 'Z:\IRP 2023\PLEXOS Solutions for PBI - KSC 9ep'
Location = r'Z:\IRP 2024\9.2 Update\9.2 Test Solutions'

#template_name = "Missouri West Rankings Template"
template_name = "KSC Rankings Full Metrics Template"
workbook_name = "KSCRankings9_2Update"

# Use lines 23 and 24 if you want every model/solution in the aforementioned folder
# Use line 25 if you only want specific model(s)/solution(s)
Solution_list = os.listdir(Location)
Solution_list = [sub.replace(' Solution.zip', '') for sub in Solution_list]
# Solution_list = ['Model MET H2C AAAB']

print("Solutions acquired.")

# Wait for the script to finish running before opening the file, as the script will stop running if the file is open and generate an error when it tries to retrieve or edit the data in the file.

#**********DO NOT GO PAST THIS POINT UNLESS YOU ARE EDITING THE SCRIPT.**********

print('Now writing new data.')
df_list=[]
# This section begins the data loop to generate the temporary files by looking up the solution files based on the location and model(s) provided.
for x in Solution_list:
    print(x)
    try:
        sol = Solution()
        sol_file = '' + Location + '/' + x + ' Solution.zip'

        sol.Connection(sol_file)

        print('Pulling Cost to Load data.')
        df_list.append(getdf(sol,columns,types,CollectionEnum.SystemRegions,'66,67,55,58,163'))

        print('Pulling Penalty Cost data.')
        df_list.append(getdf(sol,columns,types,CollectionEnum.SystemConstraints, '8'))

        sol.close()

    except:
        pass

# This section combines all the temporary data files created above into one excel file.
print('Aggregating data.')
combined_df = pd.concat(df_list)

# combined_df.shape

# This section is removing all unnecessary data, including extra columns, properties, and other data.
print('Formatting and generating data file.')

# This section reformats the file into the correct layout by making new columns, renaming old ones, and choosing what columns to publish to the final excel file.
combined_df[['Utility', 'Endpoint Name', 'Plan Name']] = combined_df['model_name'].str.split(' ', n=2, expand=True)

# combined_df = combined_df[combined_df['category_name'].isin(['Zonal Regions', 'Markets', 'NG Conversions'])]

combined_df.rename(columns=column_names, inplace=True)

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
#modified_df.rename(columns={'Total Cost': 'Total Cost ($000)'}, inplace=True)
modified_df.rename(columns={'Generator Retirement Cost': 'Retirement Cost ($000)'}, inplace=True)
modified_df.rename(columns={'Penalty Cost': 'Penalty Cost ($000)'}, inplace=True)

modified_df = modified_df[['Utility', 'Plan Name', 'Endpoint Name', 'Category', 'Unit or Zonal Region', 'Cost to Load ($000)', 'Generator Pool Revenue ($000)', 'Total Fixed Costs', 'Retirement Cost ($000)', 'Penalty Cost ($000)', 'Date', 'Period','Total Generation Cost']]
# modified_df = modified_df[['Utility', 'Endpoint Name', 'Plan Name', 'Model Name', 'Category', 'Unit or Zonal Region', 'Cost to Load ($000)', 'Generator Pool Revenue ($000)', 'Total Cost ($000)', 'Retirement Cost ($000)', 'Penalty Cost ($000)', 'Date', 'Period']]

#Dump to CSV
#print("dumping to CSV")
#modified_df.to_csv(r'Z:\IRP 2024\Model Roll Forward for 2024\Solutions\Runs031324\MOW313.csv', index=False)

#--TODO--
#dump data into template and copy template
print("Pasting Data Into Template")

app = xw.App(visible=False)
# wb = xw.Book(r"Z:/IRP 2024/Python/Templates/" + Utility + " Plan Template.xlsx")

# Rollforward templates
wb = xw.Book(r"Z:/IRP 2024/Python/Templates/"+ template_name + '.xlsx')

ws = wb.sheets['data']
ws.range("B:M").clear_contents()

# Update workbook at specified range
ws.range('B1').options(index=False).value = modified_df

# Close and save workbook
wb.save()
wb.close()
app.quit()

print("creating copy of template")

shutil.copy(r"Z:/IRP 2024/Python/Templates/"+ template_name + ".xlsx",
                    r"Z:/IRP 2024/PLEXOS Project Workbooks/" + workbook_name + ".xlsx")

print('NPVRR Rankings Data input file created.')
