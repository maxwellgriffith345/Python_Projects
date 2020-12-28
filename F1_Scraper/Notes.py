#! python3

#CREATE SOUP
import requests, bs4
res= requests.get('urllink')
res.raise_for_status() #check for erros on urllink

soup = bs4.BeautifulSoup(res.text, 'html.parser')

#bs4 commands
soup.get()
soup.find_all()
soup[index].getText()
soup[index].attrs

#F1 site

url = 'https://www.formula1.com/en/results.html'

#result tabel tag
<tabel class = "resultsarchive-table">


#race results tags/order
<tbody>
    <tr> #each row

#getting rows for race results sketch 1
table = soup.find(class_ = 'resultsarchive-table')
table_body = table.find('tbody')
rows = table_body.find_all('tr')

#getting data for all drivers
    for row in rows:
        for cols in row.find_all('td'):
            cols.getText()
#function definiton 'scrape table' can be used for all results
# for scraping races, drivers, teams
def scrape_table(soup):
    table = soup.find(class_ = 'resultsarchive-table')
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        for cols in row.find_all('td'):
            cols.getText()


#How to store the info from the table
#list of list?
# as you pull the info from row in rows
    # add that to a list row
#once that's done append that list to a list structure
#how will this effect exportin to csv
race = []
for row in rows:
    driver = []
    for cols in row.find_all('td'):
        driver.append(cols.getText())
    driver.remove('')
    driver.remove('')
    race.append(driver)

#TODO
#PROBLEMS
    #name field is dirty
    \nValtteri\nBottas\nBOT\n'
#FIX?
test the children for each 'td'
if the child of 'td' is like something
then pull that info as a seperate list and return
possible recursive use?
if len(soup.find_all("""SOME TAG""")) is > 0

#Pull links for each race for each year
for year in years:
    for race in year:
        #scrape table
#scroll container
resultsarchive-filter-container
#pull year_cat_race
div.resultsarchive-filter-wrap:nth-child(1)

div.resultsarchive-filter-wrap:nth-child(3) > ul:nth-child(1) > li:nth-child(1)


#good Pull each race from a year
import requests, bs4
website = requests.get('https://www.formula1.com/en/results.html')
website.raise_for_status()
soup = bs4.BeautifulSoup(website.text, 'html.parser')
year_cat_race = soup.find_all('div', class_ = 'resultsarchive-filter-container')

racelink_2020 = []
for race in year_cat_race[2].find_all('a'):
	racelink_2020.append(race.get('href'))
url = 'https://www.formula1.com'
for i, val in enumerate(racelink_2020):
	racelink_2020[i] = url+val


#best way to store year and race data?
tuple? (year, racelink_list) #do you need the year info?
list of list [ranklink_list,racelink_list]

#flow of program?
go to year link
    go to race link
        scrap table
        export table to csv

for years in year_list
    open year url
    pull all race_links race_list
    for race_link in race_list
        soup = get_soup(race_link)
        pull race name
        scrape race tabel into race_results []
        write to csv (race_name, race_results)


"""WORING WITH CSV"""
#read from csv
import csv
file = open('example.csv') #open file
file_reader = csv.reader(file) #read file
data = list(file_reader) #export csv file to a list
#acces teh data by using data[row][col]

#write to csv
import csv
outputfile = open('output.csv','w',newline='')
outputwriter = csv.wrtier(outputfile)
outputwriter.writerow(['spam','eggs','bacon','ham'])
outputWriter.writerow(['Hello, world!', 'eggs', 'bacon', 'ham'])
outputWriter.writerow([1, 2, 3.141592, 4])
outputFile.close()

#create new folder using os
# importing os module
import os

# Directory
directory = "GeeksForGeeks"

# Parent Directory path
parent_dir = "D:/Pycharm projects/"

# Path
path = os.path.join(parent_dir, directory)

# Create the directory
# 'GeeksForGeeks' in
# '/home / User / Documents'
os.mkdir(path)
print("Directory '% s' created" % directory)

# if directory / file that
# is to be created already
# exists then 'FileExistsError'
# will be raised by os.mkdir() method  
