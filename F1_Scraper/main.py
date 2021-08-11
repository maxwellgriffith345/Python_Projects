
"""
OUTLINE

Create master_df

Get all the year links

Loop over Year
For Year:
    Pull year
    Pull race_names
    Pull race_links
    Create list of tuples of (race_name, race_link) #use zip method
        merged_list = tuple(zip(list1, list2))
    For nam, link in mered_list:
        pull table
        clean up table
        add year and race columns
        append to master df (df.append)
            df.append(df2, ignore_index=True)

write main df to csv  """

#!/usr/bin/env python3

import requests,bs4, csv, os
import numpy as np
import pandas as pd
import f1scraper1 as scrape

main_url = 'https://www.formula1.com/en/results.html'
main_soup = scrape.get_soup(main_url)
year_links = scrape.get_year_links(main_soup) #get all year links

column_names = ['Pos', 'No', 'Driver', 'Car', 'Laps', 'Time/Retired', 'PTS', 'year',
       'race']
main_df = pd.DataFrame(columns = column_names)

#GET ALL RACE RESULTS BY YEAR
for year in year_links:
    yeardate = scrape.get_year(year)
    year_soup = scrape.get_soup(year)
    racelinks = scrape.get_race_links(year_soup)
    racenames = scrape.get_race_names(year_soup)
    name_link = tuple(zip(racenames,racelinks))
    name_link.pop(0)
    for name, link in name_link:
        table = pd.read_html(link)
        df = table[0]
        df.drop(['Unnamed: 0','Unnamed: 8'], axis =1, inplace = True)
        df[['year', 'race']] = yeardate, name
        main_df = main_df.append(df)

main_df.to_csv('f1.csv', index =False)

#need to skip first link which is "all"
