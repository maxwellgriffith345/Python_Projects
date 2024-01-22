import os, sys, clr
import pandas as pd
import glob
from openpyxl import load_workbook
import pathlib
import xlwings as xw
import shutil
from datetime import datetime, timedelta
import numpy as np
from System import DateTime, String

sys.path.append(r'C:\Program Files\Energy Exemplar\PLEXOS 9.0 API')
clr.AddReference('PLEXOS_NET.Core')
clr.AddReference('EEUTILITY')
clr.AddReference('EnergyExemplar.PLEXOS.Utility')

from PLEXOS_NET.Core import *
from EEUTILITY.Enums import *
from EnergyExemplar.PLEXOS.Utility.Enums import *

#HELPER FUNCTIONS
def getgendf(sol, date, columns, types, categories):
    datefrom=date[0]
    dateto=date[1] +' 23:00'
    results_listyear = sol.QueryToList(
        SimulationPhaseEnum.LTPlan, \
        CollectionEnum.SystemGenerators, \
        '', \
        '', \
        PeriodEnum.Interval, \
        SeriesTypeEnum.Values, \
        '', \
        DateTime.Parse(datefrom), \
        DateTime.Parse(dateto), \
        '', \
        '', \
        '', \
        AggregationEnum.Category,\
        categories)
    
    df=pd.DataFrame([[row.GetProperty.Overloads[String](n) for n in columns] for row in results_listyear], columns=columns)
    #clean up data types
    df = df.astype(types)
    df=df.astype({'_date':'datetime64[ns]'})
    df=df[(df["_date"]>=datefrom)]
    return df

def getloaddf(sol, date, columns, types):
    datefrom=date[0]
    dateto=date[1] +' 23:00'
    results_listyear = sol.QueryToList(
        SimulationPhaseEnum.LTPlan, \
        CollectionEnum.SystemRegions, \
        '', \
        '', \
        PeriodEnum.Interval, \
        SeriesTypeEnum.Values, \
        '', \
        DateTime.Parse(datefrom), \
        DateTime.Parse(dateto), \
        '', \
        '', \
        '', \
        AggregationEnum.Category)
    
    df=pd.DataFrame([[row.GetProperty.Overloads[String](n) for n in columns] for row in results_listyear], columns=columns)
    #clean up data types
    df = df.astype(types)
    df=df.astype({'_date':'datetime64[ns]'})
    df=df[(df["_date"]>=datefrom)]
    return df

def getbatdf(sol, date, columns, types):
    datefrom=date[0]
    dateto=date[1] +' 23:00'
    results_listyear = sol.QueryToList(
        SimulationPhaseEnum.LTPlan, \
        CollectionEnum.SystemBatteries, \
        '', \
        '', \
        PeriodEnum.Interval, \
        SeriesTypeEnum.Values, \
        '', \
        DateTime.Parse(datefrom), \
        DateTime.Parse(dateto), \
        '', \
        '', \
        '', \
        AggregationEnum.Category)
    
    df=pd.DataFrame([[row.GetProperty.Overloads[String](n) for n in columns] for row in results_listyear], columns=columns)
    #clean up data types
    df = df.astype(types)
    df=df.astype({'_date':'datetime64[ns]'})
    df=df[(df["_date"]>=datefrom)]
    return df
    
def get_year_range(year):
    start_date = datetime(year,1,1).strftime('%Y-%m-%d')
    end_date = datetime(year,12,31).strftime('%Y-%m-%d')
    return start_date, end_date


#CONNECT TO SOLUTION
Location = r"Z:\IRP 2024\Training for MG\HourlyGen\Solutions"
x = "Model MOW M2C ECAA Plan"
sol = Solution()
sol_file = '' + Location + '/' + x + ' Solution.zip'
sol.Connection(sol_file)

#SET VARIABLES
types = {'_date': "string",'category_name': "category", "value": np.float32}
columns=['_date','category_name','value']
gencats = "Build CC, Build CT, Build Capacity, Build Solar, Build Wind, Coal, DSM Existing, DSM Potential, Gas, LandfillGas, Oil, Solar, Wind PPA"

#SET DATES
Dates=[(get_year_range(year)) for year in range(2024,2044)]

#Pull Gen, Load and Bat data
print("Pulling Generation Data")
gen_dfs = pd.concat(getgendf(sol, date,columns,types, gencats) for date in Dates)
print("Pulling Load Data")
load_dfs = pd.concat(getloaddf(sol, date, columns,types) for date in Dates)
print("Pulling Battery Data")
bat_dfs = pd.concat(getbatdf(sol, date, columns,types) for date in Dates)

sol.Close()
#COMBINE DATA
combined_df=pd.concat([gen_dfs, load_dfs, bat_dfs])

#CREATE YEAR AND HOUR COLUMNS
combined_df["Year"]=combined_df["_date"].dt.year
combined_df["Hour"]=combined_df["_date"].dt.hour

#PIVOT
pivot_table = combined_df.pivot_table(values="value", index=["Year", "Hour"], columns="category_name", aggfunc="mean")
pivot_table.reset_index(inplace=True)
new_pivot=pd.DataFrame(pivot_table.to_records(index=False))

#--TODO ---OUTPUT DATA
new_pivot.to_csv(r'Z:\IRP 2024\Training for MG\HourlyGen\20yearPivotCat2.csv',index=False)
print("Script Finished")
#-----------TODO--------------
