#################################
##### Name:
##### Uniqname:
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category='', name='', address='', zipcode='', phone=''):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"

URL_CACHE = {}
url = 'search'

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    if url in URL_CACHE.keys():
        print('Using cache')
        return URL_CACHE[url]
    else:
        html = requests.get("https://www.nps.gov/index.htm").text
        soup = BeautifulSoup(html, 'html.parser')
        select_state = soup.find(class_='SearchBar-keywordSearch',role='menu').find_all('li')
        state = {}
        select_url = soup.find(class_='SearchBar-keywordSearch',role='menu').find_all('a')
    #select_nation = select_div[0].contents[1]
    #for item in select_state:
    #    print(item.text.strip())
    #for item in select_url:
        #item = f"https://www.nps.gov{item['href']}"
        #print((item))

        n = 0
        for item in select_state:
            item = item.string.lower()
            state[item]=f"https://www.nps.gov{select_url[n]['href']}"
            n += 1
        URL_CACHE[url]=state
        return URL_CACHE[url]
  
SITE_CACHE = {}

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    if site_url in SITE_CACHE.keys():
        print('Using cache')
        return SITE_CACHE[site_url]
    else:
        html = requests.get(site_url).text
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.find(class_='Hero-title').text
        category = soup.find(class_='Hero-designation').text
        address_loc = soup.find(itemprop='addressLocality').text
        address_region = soup.find(itemprop='addressRegion').text
        address = f"{address_loc}, {address_region}"
        zipcode = soup.find(itemprop='postalCode').text.strip()
        phone = soup.find(itemprop='telephone').text.strip()
    
        national_site = NationalSite(category, name, address, zipcode, phone)
        SITE_CACHE[site_url]=national_site
    return SITE_CACHE[site_url]


STATE_CACHE = {}  

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    if state_url in STATE_CACHE.keys():
        print('Using cache')
    else:
        html = requests.get(state_url).text
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.find(id='list_parks').find_all('h3')
        site_list=[]
        for item in name:
            item = item.find('a')['href']
        
            url = f"https://www.nps.gov{item}index.htm"
            print('Fetching')
            site_list.append(get_site_instance(url))
        STATE_CACHE[state_url]=site_list
    
    return STATE_CACHE[state_url]

ZIP_CACHE = {}

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    base_url = "http://www.mapquestapi.com/search/v2/radius"
    site_origin = site_object.zipcode
    api_key = secrets.API_KEY
    params = {
        "key":api_key,
        "origin":site_origin,
        "radius":10,
        "maxMatches":10,
        "ambiguities":"ignore",
        "outFormat":"json"
    }
    if site_origin in ZIP_CACHE.keys():
        print('Using cache')
        for item in ZIP_CACHE[site_origin]['searchResults']:
            if item['fields']['group_sic_code_name']:
                category = item['fields']['group_sic_code_name']
            else:
                category = 'no category'
            if item['fields']['address']:
                address = item['fields']['address']
            else:
                address = "no address"
            if item['fields']['city']:
                city = item['fields']['city']
            else:
                city = 'no city'
            print(f"- {item['name']} ({category}): {address}, {city}") 
        return ZIP_CACHE[site_origin]

    else:
        response = requests.get(base_url, params)
        result = response.json()
        ZIP_CACHE[site_origin] = result
        print('Fetching')
        for item in ZIP_CACHE[site_origin]['searchResults']:
            if item['fields']['group_sic_code_name']:
                category = item['fields']['group_sic_code_name']
            else:
                category = 'no category'
            if item['fields']['address']:
                address = item['fields']['address']
            else:
                address = "no address"
            if item['fields']['city']:
                city = item['fields']['city']
            else:
                city = 'no city'
            print(f"- {item['name']} ({category}): {address}, {city}") 
        return ZIP_CACHE[site_origin]

   
    

if __name__ == "__main__":
    # Part 3

    state_dic = build_state_url_dict()
    count = 0
    while(True):
        if count == 0:
            text = input('Enter a state name (e.g. Michigan, michigan) or "exit": ')
            if text == 'exit':
                print('Bye!')
                break
            else:
                text = text.lower()
                if text in state_dic.keys():
                    url = state_dic[text]
                    site_list = get_sites_for_state(url)
                    num = 1
                    print('-------------------------')
                    print('List of national sites in Michigan')
                    print('-------------------------')
                    for item in site_list:
                        print(f'[{num}] {item.name} ({item.category}): {item.address} {item.zipcode}')
                        num += 1
                    count = 1
                else:
                    print('[Error] Enter proper state name')
        if count == 1:
            text = input('Choose the number for detail search or "exit" or "back": ')
            if text == 'exit':
                print('Bye !')
                break
            elif text == 'back':
                count = 0
            else:
                if text.isdigit():
                    number_int = int(text)
                    if number_int > num or number_int < 1:
                        print('[Error] Invalid input')
                    else:
                        site_obj = site_list[number_int-1]
                        print('---------------------------------')
                        print(f"Places near {site_obj.name}")
                        print('---------------------------------')
                        near_site = get_nearby_places(site_obj)
                else:
                    print('[Error] Invalid input')


        


    # Part 4
    '''
    site_mi2 = get_site_instance('https://www.nps.gov/slbe/index.htm')
    near_mi = get_nearby_places(site_mi2)
    '''
    '''
    for item in near_mi['searchResults']:
        if item['fields']['group_sic_code_name']:
            category = item['fields']['group_sic_code_name']
        else:
            category = 'no category'
        if item['fields']['address']:
            address = item['fields']['address']
        else:
            address = "no address"
        if item['fields']['city']:
            city = item['fields']['city']
        else:
            city = 'no city'
        print(f"- {item['name']} ({category}): {address}, {city}")
        '''












    