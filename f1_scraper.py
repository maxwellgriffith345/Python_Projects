
def get_soup(url):
    website= requests.get(url)
    website.raise_for_status() #check for erros on urllink
    soup = bs4.BeautifulSoup(website.text, 'html.parser')
    return(soup)

def scrape_links(soup):
    link_list = []
    #fetch href
    for link in soup.find_all('a'):
        link_list.append(link.get('href'))

    short_url = 'https://www.formula1.com'
    for i, val in enumerate(link_list):
        link_list[i] = short_url+val
    return(link_list)

#SHOULD THE get FUNCTIONS TAKE soup or url AS A PARAMETER? OVER LOADING IN PYTHON?
def get_year_links(soup):
    year_soup = soup.select('div.resultsarchive-filter-wrap')[0]
    return(scrape_links(year_soup))

def get_cat_links(soup):
    cat_soup = soup.select('div.resultsarchive-filter-wrap')[1]
    return(scrape_links(cat_soup))

def get_race_links(soup):
    race_soup = soup.select('div.resultsarchive-filter-wrap')[2]
    return(scrape_links(race_soup))


def scrape_table(soup): #very slow 
    table = []
    res_table = soup.find(class_ = 'resultsarchive-table')
    table_body = res_table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        entry = []
        for cols in row.find_all('td'):
            if len(cols.select('span')) > 1:
                for text in cols.select('span'):
                    entry.append(text.getText())
            else: 
                entry.append(cols.getText())
        entry.remove('')
        entry.remove('')
        table.append(entry)
    return(table)

def write_csv(filename, table):
    outfile = open(filename, 'w', newline='')
    outwriter = csv.writer(outfile)
    for row in table:
        outwriter.writerow(row)

def get_file_name(url): #gotta be a faster way to get this info, how to deal with duplicate race names?
    new_url = url
    stripurl = new_url.lstrip('https://www.formula1.com/en/results.html/')
    spliturl = stripurl.split('/') #5sections
    if(len(spliturl)) < 5:
        year_race = spliturl[0]+'all'
    else:
        year_race = spliturl[0]+spliturl[3]
    return(year_race)

#MAIN
import requests, bs4,csv

url = 'https://www.formula1.com/en/results.html/2019/races.html'

clean_url = 'https://www.formula1.com'

soup = get_soup(url)

yearlinks = get_year_links(soup)
racelinks_2019 = get_race_links(soup)

hungary2020 = scrape_table(get_soup(racelinks_2019[3]))

#for link in racelinks_2019:
 #   print(get_file_name(link))

#write_csv('hungary2020.csv', hungary2020)

#for driver in hungary2020:
 #   print(driver)

for link in racelinks_2019:
    file_name = get_file_name(link)+'.csv'
    race_soup = get_soup(link)
    race_table = scrape_table(race_soup)
    write_csv(file_name,race_table)

#TODDO NEED A FUNCTION THAT CREATES A NEW FOLDER FOR EACH YEAR
#TODO for 'all' races formating is weird
#TODO it be slow as heck