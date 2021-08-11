import pandas as pd

#scrape from htlm address

url = 'https://www.formula1.com/en/results.html/2021/races/1067/monaco.html'
tables = pd.read_html(url)  #tables is a list of df
df = tables[0] #gets you the df

#clean up
df.drop(['Unnamed: 0','Unnamed: 8'], axis =1, inplace = True)

#does not include year or track name
#need to pull track name and year and append to each row
def get_year_race(url):
    stripurl= url.lstrip('https://www.formula1.com/en/results.html/').rstrip('.html')
    spliturl = stripurl.split('/')
    year_race = (spliturl[0], spliturl[3])
    return year_race

#problem duplicate race names

year_race = get_year_race(url)

#add year race to df
df[['year', 'race']]=year_race



#get the race names
main_url = 'https://www.formula1.com/en/results.html'
website = requests.get(main_url)
website.raise_for_status()
soup = bs4.BeautifulSoup(website.text, 'html.parser')

def get_race_names(soup):
    race_soup = soup.select('div.resultsarchive-filter-wrap')[2]
    race_list = []
    for span in race_soup.find_all('span'):
        race_list.append(span.get_text())
    return race_list

#PULL RACE DATES
#PULL TRACK NAME AND CITY
#Scrape all drivers nationalities- https://en.wikipedia.org/wiki/List_of_Formula_One_drivers
