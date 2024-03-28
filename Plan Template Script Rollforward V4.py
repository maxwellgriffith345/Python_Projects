#This script is used to create the Regional and Build data files
import os, sys, clr
import pandas as pd
from openpyxl import load_workbook
import pathlib
import xlwings as xw
import shutil
from System import DateTime, String
import numpy as np
from datetime import datetime, timedelta

sys.path.append(r'C:\Program Files\Energy Exemplar\PLEXOS 9.0 API')
clr.AddReference('PLEXOS_NET.Core')
clr.AddReference('EEUTILITY')
clr.AddReference('EnergyExemplar.PLEXOS.Utility')

from PLEXOS_NET.Core import *
from EEUTILITY.Enums import *
from EnergyExemplar.PLEXOS.Utility.Enums import *

#--HELPER FUNCTIONS--
def getdf(sol, columns, types, collection, properties=''):
    results_listyear = sol.QueryToList(
        SimulationPhaseEnum.LTPlan, \
        collection, \
        '', \
        '', \
        PeriodEnum.FiscalYear, \
        SeriesTypeEnum.Periods, \
        properties)
    df = pd.DataFrame([[row.GetProperty.Overloads[String](n) for n in columns] for row in results_listyear],
                      columns=columns)
    # clean up data types
    df = df.astype(types)
    return df

def getquarterlydf(sol, columns, types,collection, properties=''):
    results_listyear = sol.QueryToList(
        SimulationPhaseEnum.LTPlan, \
        collection, \
        '', \
        '', \
        PeriodEnum.Quarter, \
        SeriesTypeEnum.Values, \
        properties)
    df = pd.DataFrame([[row.GetProperty.Overloads[String](n) for n in columns] for row in results_listyear],
                      columns=columns)
    # clean up data types
    df = df.astype(types)
    df['_date']=pd.to_datetime(df['_date'], format='%m/%d/%Y %I:%M:%S %p')
    return df


columns = ['child_name','property_name','parent_name','unit_name','band_id','collection_name','category_name',
           r'12\\31\\2024 12:00 AM', r'12\\31\\2025 12:00 AM', r'12\\31\\2026 12:00 AM',
           r'12\\31\\2027 12:00 AM', r'12\\31\\2028 12:00 AM', r'12\\31\\2029 12:00 AM',
           r'12\\31\\2030 12:00 AM', r'12\\31\\2031 12:00 AM', r'12\\31\\2032 12:00 AM',
           r'12\\31\\2033 12:00 AM', r'12\\31\\2034 12:00 AM', r'12\\31\\2035 12:00 AM',
           r'12\\31\\2036 12:00 AM', r'12\\31\\2037 12:00 AM', r'12\\31\\2038 12:00 AM',
           r'12\\31\\2039 12:00 AM', r'12\\31\\2040 12:00 AM', r'12\\31\\2041 12:00 AM',
           r'12\\31\\2042 12:00 AM', r'12\\31\\2043 12:00 AM']
column_names = {'child_name': 'Child Name','property_name': 'Property','parent_name': 'Parent Name','unit_name': 'Units',
                'band_id': 'Band','collection_name': 'Collection','category_name': 'Category',
                r'12\\31\\2024 12:00 AM': '2024', r'12\\31\\2025 12:00 AM': '2025', r'12\\31\\2026 12:00 AM':'2026',
                r'12\\31\\2027 12:00 AM': '2027', r'12\\31\\2028 12:00 AM' : '2028', r'12\\31\\2029 12:00 AM': '2029',
                r'12\\31\\2030 12:00 AM': '2030', r'12\\31\\2031 12:00 AM': '2031', r'12\\31\\2032 12:00 AM': '2032',
                r'12\\31\\2033 12:00 AM': '2033', r'12\\31\\2034 12:00 AM': '2034', r'12\\31\\2035 12:00 AM': '2035',
                r'12\\31\\2036 12:00 AM': '2036', r'12\\31\\2037 12:00 AM': '2037', r'12\\31\\2038 12:00 AM': '2038',
                r'12\\31\\2039 12:00 AM': '2039', r'12\\31\\2040 12:00 AM': '2040', r'12\\31\\2041 12:00 AM': '2041',
                r'12\\31\\2042 12:00 AM': '2042', r'12\\31\\2043 12:00 AM': '2043'
                }
types = {'child_name': "string",'property_name': "string",'parent_name': "string",'unit_name':"string",'collection_name': "string",
           'category_name': "string",
           r'12\\31\\2024 12:00 AM':np.float32, r'12\\31\\2025 12:00 AM':np.float32, r'12\\31\\2026 12:00 AM':np.float32,
           r'12\\31\\2027 12:00 AM':np.float32, r'12\\31\\2028 12:00 AM':np.float32, r'12\\31\\2029 12:00 AM':np.float32,
           r'12\\31\\2030 12:00 AM':np.float32, r'12\\31\\2031 12:00 AM':np.float32, r'12\\31\\2032 12:00 AM':np.float32,
           r'12\\31\\2033 12:00 AM':np.float32, r'12\\31\\2034 12:00 AM':np.float32, r'12\\31\\2035 12:00 AM':np.float32,
           r'12\\31\\2036 12:00 AM':np.float32, r'12\\31\\2037 12:00 AM':np.float32, r'12\\31\\2038 12:00 AM':np.float32,
           r'12\\31\\2039 12:00 AM':np.float32, r'12\\31\\2040 12:00 AM':np.float32, r'12\\31\\2041 12:00 AM':np.float32,
           r'12\\31\\2042 12:00 AM':np.float32, r'12\\31\\2043 12:00 AM':np.float32}

columnsquarter = ['parent_name','child_name', 'property_name', 'unit_name', 'band_id', 'collection_name',
                  'category_name', '_date', 'value']

column_namesquarter={'child_name': 'Child Name','property_name': 'Property','parent_name': 'Parent Name',
                     'unit_name': 'Units','band_id': 'Band','collection_name': 'Collection','category_name': 'Category',
                     '_date': 'Quarter','value': 'Value'}

typesquarter = {'child_name': "string",'property_name': "string",'unit_name':"string",'collection_name': "string",
           'category_name': "string", 'value': np.float32, '_date': "string"}

#Enter the locations for the solution files you want
Location = r'Z:\IRP 2024\Mode\Solutions\'

#model solutions files you want
Solution_list = os.listdir(Location)
Solution_list = [sub.replace(' Solution.zip', '') for sub in Solution_list]

for x in Solution_list:
    print("******"+x+"******")
    Utility = x.split(' ')[1]
    df_list=[]
    try:
        sol = Solution()
        sol_file = '' + Location + '/' + x + ' Solution.zip'
        sol.Connection(sol_file)

        print('Pulling Generator data.')
        df_list.append(getdf(sol, columns, types, CollectionEnum.SystemGenerators))

        print('Pulling Battery data (if it exists).')
        if sol.CategoryExists(ClassEnum.Battery, ''):
            df_list.append(getdf(sol, columns, types, CollectionEnum.SystemBatteries))

        print("Pulling Load Data")
        df_list.append(getdf(sol, columns, types, CollectionEnum.SystemRegions))

        print('Pulling Emissions data.')
        df_list.append(getdf(sol, columns, types, CollectionEnum.SystemEmissions))

        print('Pulling Constraint data.')
        df_list.append(getdf(sol, columns, types, CollectionEnum.SystemConstraints, '8'))

        print('Aggregating data.')
        combined_df = pd.concat(df_list)

        combined_df.rename(columns=column_names, inplace=True)

        combined_df = combined_df[['Parent Name', 'Collection', 'Child Name', 'Category', 'Property', 'Band', 'Units',
                                    '2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033',
                                   '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041', '2042', '2043']]

        print("Pulling Quarterly Firm Capacity Data")
        quarterfirmcap = getquarterlydf(sol, columnsquarter, typesquarter, CollectionEnum.SystemGenerators, '207')
        df_list =[quarterfirmcap]

        print("Pulling Quarterly Firm Generation Capacity Data (if it exists).")
        if sol.CategoryExists(ClassEnum.Battery, ''):
            df_list.append(getquarterlydf(sol, columnsquarter, typesquarter, CollectionEnum.SystemBatteries))

        print("Pulling Quarterly Planning Peak Load Data")
        df_list.append(getquarterlydf(sol, columnsquarter, typesquarter, CollectionEnum.SystemRegions, '146,116'))

        print('Aggregating data.')
        combined_df2 = pd.concat(df_list)

        #This section is removing all unnecessary data, including extra columns, properties, and other data.
        print('Formatting and generating data file.')
        combined_df2 = combined_df2[combined_df2['property_name'].isin(['Firm Capacity', 'Firm Generation Capacity', 'Planning Peak Load'])]

        combined_df2.rename(columns=column_namesquarter, inplace=True)

        combined_df2 = combined_df2[['Parent Name', 'Collection', 'Child Name', 'Category', 'Property', 'Band', 'Quarter',
                                   'Value', 'Units']]

        sol.Close()
#-------This section pastes the data into the Plan Template--------
        print("Pasting Sample Output data.")

        app = xw.App(visible=False)
        wb = xw.Book(r"Z:/IRP 2024/Python/Templates/" + Utility + " Plan Template2024.xlsx")

        ws = wb.sheets['SampleOutput']
        ws.range("F:AF").clear_contents()

        #Update workbook at specified range
        ws.range('F1').options(index=False).value = combined_df

        print("Sample Output of plan workbook created.")

        print("Pasting Sample Output 2 data.")
        ws = wb.sheets['SampleOutput2']
        ws.range("C:K").clear_contents()

        #Update workbook at specified range
        ws.range('C1').options(index=False).value = combined_df2

        print("Sample Output 2 of plan workbook created.")
        print("Updating model name on the Summary sheet.")

        x = x.replace('Model ', '')

        ws = wb.sheets['Summary']
        ws.range("C1:C1").clear_contents()

        plan_name = x.replace(' Plan', '')

        #Update workbook at specified range
        ws.range('C1').options(index=False).value = plan_name

        #Close and save workbook
        wb.save()
        wb.close()
        app.quit()

        #Rollforward Template
        shutil.copy(r"Z:/IRP 2024/Python/Templates/" + Utility + " Plan Template2024.xlsx",
                    r"Z:/IRP 2024/PLEXOS Plan Workbooks/" + x + ".xlsx")


        print("Model name on the Summary sheet is updated.")
        print("Plan Workbook is now available.")

    except:
        pass
        
print("Script finished. Workbooks created in IRP 2024 -> PLEXOS Plan Workbooks")
