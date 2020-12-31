
def get_soup(url):
    website= requests.get(url)
    website.raise_for_status()
    soup = bs4.BeautifulSoup(website.text, 'html.parser')
    return(soup)

def scrape_links(soup):
    link_list = []
    for link in soup.find_all('a'):
        link_list.append(link.get('href'))
    short_url = 'https://www.formula1.com'
    for i, val in enumerate(link_list):
        link_list[i] = short_url+val
    return(link_list)

def get_year_links(soup):
    year_soup = soup.select('div.resultsarchive-filter-wrap')[0]
    return(scrape_links(year_soup))

def get_cat_links(soup):
    cat_soup = soup.select('div.resultsarchive-filter-wrap')[1]
    return(scrape_links(cat_soup))

#NEED TO CHANGE THE NAME OF THIS FUNCTION
def get_race_links(soup):
    race_soup = soup.select('div.resultsarchive-filter-wrap')[2]
    return(scrape_links(race_soup))

def scrape_table(soup): #slow 
    table = []
    res_table = soup.find(class_ = 'resultsarchive-table')
    table_body = res_table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        entry = []
        for cols in row.find_all('td'):
            if len(cols.select('span')) > 1:
                for text in cols.select('span'):
                    entry.append((text.getText()).strip())       
            else: 
                entry.append((cols.getText()).strip())
        entry.remove('')
        entry.remove('')
        table.append(entry)
    return(table)

def write_csv(filename, table):
    outfile = open(filename, 'w', newline='')
    outwriter = csv.writer(outfile)
    for row in table:
        outwriter.writerow(row)

def get_file_name(url,path): 
    #gotta be a faster way to get this info, 
    #how to deal with duplicate race names?
    new_url = url
    stripurl = new_url.lstrip('https://www.formula1.com/en/results.html/').rstrip('.html')
    spliturl = stripurl.split('/') #5sections
    if(len(spliturl)) < 3:
        year_race = spliturl[0]+'all'
    else:
        year_race = spliturl[0]+spliturl[3]
    return(path+year_race+'.csv')

def get_driver_linklist(year_link):
    year_soup = get_soup(year_link)
    catlinks = get_cat_links(year_soup)
    driverlinks = catlinks[1]
    driversoup = get_soup(driverlinks)
    driverslinklist = get_race_links(driversoup)
    return(driverslinklist)


#MAIN
import requests,bs4,csv,os

driver_path = '/Users/maxwellgriffith/Documents/MyProjects/Python_Projects/F1_Scraper/driveresults/'
race_path = '/Users/maxwellgriffith/Documents/MyProjects/Python_Projects/F1_Scraper/raceresults/'
main_url = 'https://www.formula1.com/en/results.html'
main_soup = get_soup(main_url)

#GET DRIVER RESULTS FOR YEAR
year_links = get_year_links(main_soup) #get all year links
yearlink2019 = year_links[1] #get link for 2019

driverlinks2019 = get_driver_linklist(yearlink2019)

for driverlink in driverlinks2019:
    filename = get_file_name(driverlink, driver_path)
    driver_soup = get_soup(driverlink)
    driver_table = scrape_table(driver_soup)
    write_csv(filename,driver_table)

"""
#GET RACE RESULTS FOR YEAR

yearlinks = get_year_links(soup)
racelinks_2019 = get_race_links(soup)

hungary2020 = scrape_table(get_soup(racelinks_2019[0]))

for link in racelinks_2019:
    file_name = get_file_name(link,path)
    race_soup = get_soup(link)
    race_table = scrape_table(race_soup)
    write_csv(file_name,race_table)
"""
