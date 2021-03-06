import random
import re
import requests

from decimal import Decimal
from lxml import html
from re import sub
from urllib import pathname2url

URL = '''http://www.zillow.com'''
SEARCH_FOR_SALE_PATH = '''homes/for_sale'''
GET_PROPERTY_BY_ZPID_PATH = '''homes'''
GET_SIMILAR_HOMES_FOR_SALE_PATH = '''homedetails'''
IMAGE_URL_REGEX_PATTERN = '"z_listing_image_url":"([^"]+)",'
SIMILAR_HOMES_ZPID_REGEX_PATTERN ='\/(\d+)_zpid'

SEARCH_XPATH_FOR_ZPID = '''//div[@id='list-results']/div[@id='search-results']/ul[@class='photo-cards']/li/article/@id'''
GET_INFO_XPATH_FOR_STREET_ADDR = '''//header[@class='zsg-content-item']/h1[@class='zsg-h1']/div[@class='zsg-h1 hdp-home-header-st-addr']/text()'''
GET_INFO_XPATH_FOR_CITY_STATE_ZIP = '''//header[@class='zsg-content-item']/h1[@class='zsg-h1']/div[@class='zsg-h2']/text()'''
GET_INFO_XPATH_FOR_TYPE = '''//div[@class='fact-group zsg-lg-1-3 zsg-md-1-2'][1]/div[@class='zsg-media-bd']/div[@class='fact-value']/text()'''
GET_INFO_XPATH_FOR_BEDROOM = '''//header[@class='zsg-content-item']/h3/span[2]/text()'''
GET_INFO_XPATH_FOR_BATHROOM = '''//header[@class='zsg-content-item']/h3/span[4]/text()'''
GET_INFO_XPATH_FOR_SIZE = '''//header[@class='zsg-content-item']/h3/span[6]/text()'''
GET_INFO_XPATH_FOR_SALE = '''//div[@class='estimates']/div/div[@class='status']'''
GET_INFO_XPATH_LIST_FOR_PRICE = '''//div[@class='estimates']/div/div[@class='price']/span/text()'''
GET_INFO_XPATH_DESCRIPTION = '''//div[@class='character-count-text-fold-container']/div[1]/text()'''
GET_INFO_XPATH_FOR_FACTS = '''//div[@class='fact-group zsg-lg-1-3 zsg-md-1-2']/div[@class='zsg-media-bd']/div/text()'''
GET_SIMILAR_HOMES_FOR_SALE_XPATH = '''//div[@class='zsg-photo-card-content zsg-aspect-ratio-content']/a/@href'''


# GET_INFO_XPATH_FOR_LATITUDE = '''//div[@class='google-ad-config']'''
GET_INFO_XPATH_FOR_LATITUDE = '''//span[@itemprop='geo']/meta[@itemprop='latitude']/@content'''
GET_INFO_XPATH_FOR_LONGITUDE = '''//span[@itemprop='geo']/meta[@itemprop='longitude']/@content'''
GET_INFO_XPATH_FOR_ADDITIONAL_FACTS = '''//div[@class='fact-group-container zsg-content-component z-moreless-content hide']/ul/li/text()'''


# Load user agents
USER_AGENTS_FILE = '../common/user_agents.txt'
USER_AGENTS = []

with open(USER_AGENTS_FILE, 'rb') as uaf:
    for ua in uaf.readlines():
        if ua:
            USER_AGENTS.append(ua.strip()[1:-1-1])
random.shuffle(USER_AGENTS)

def build_url(url, path):
    if url[-1] == '/':
        url = url[:-1]
    return '%s/%s' % (url, path)

def getHeaders():
    ua = random.choice(USER_AGENTS)  # select a random user agent
    headers = {
        "Connection" : "close",
        "User-Agent" : ua
    }
    return headers

def search_zillow(request_url, xpath):
    session_requests = requests.session()
    response = session_requests.get(request_url, headers=getHeaders())
    tree = html.fromstring(response.content)
    return tree.xpath(xpath)

""" Search properties by zip code """
def search_zillow_by_zip(zipcode):
    request_url = '%s/%s' % (build_url(URL, SEARCH_FOR_SALE_PATH), str(zipcode))
    raw_result = search_zillow(request_url, SEARCH_XPATH_FOR_ZPID)
    return [x.replace('zpid_', '') for x in raw_result]

""" Search properties by city and state """
def search_zillow_by_city_state(city, state):
    city_state = pathname2url('%s %s' % (city, state))
    request_url = '%s/%s' % (build_url(URL, SEARCH_FOR_SALE_PATH), city_state)
    raw_result =  search_zillow(request_url, SEARCH_XPATH_FOR_ZPID)
    return [x.replace('zpid_', '') for x in raw_result]

""" Get Similar homes for sale """
def get_similar_homes_for_sale_by_id(zpid):
    request_url = '%s/%s_zpid' % (build_url(URL, GET_SIMILAR_HOMES_FOR_SALE_PATH), str(zpid))
    raw_result = search_zillow(request_url, GET_SIMILAR_HOMES_FOR_SALE_XPATH)
    return [re.search(SIMILAR_HOMES_ZPID_REGEX_PATTERN, x).group(1) for x in raw_result]

""" Get property information by Zillow Property ID (zpid) """
def get_property_by_zpid(zpid):
    request_url = '%s/%s_zpid' % (build_url(URL, GET_PROPERTY_BY_ZPID_PATH), str(zpid))
    session_requests = requests.session()
    response = session_requests.get(request_url, headers=getHeaders())
    try:
        tree = html.fromstring(response.content)
    except Exception:
        return {}

    # Street address
    street_address = None
    try:
        street_address = tree.xpath(GET_INFO_XPATH_FOR_STREET_ADDR)[0].strip(', ')
    except Exception:
        pass

    # City, state and zipcode
    city_state_zip = None
    city = None
    state = None
    zipcode = None
    try:
        city_state_zip = tree.xpath(GET_INFO_XPATH_FOR_CITY_STATE_ZIP)[0]
        city = city_state_zip.split(',')[0].strip(', ')
        state = city_state_zip.split(',')[1].split(' ')[1].strip(', ')
        zipcode = city_state_zip.split(',')[1].split(' ')[2].strip(', ')
    except Exception:
        pass

    # Type: Condo, Town hourse, Single family etc.
    property_type = None
    try:
        property_type = tree.xpath(GET_INFO_XPATH_FOR_TYPE)[0]
    except Exception:
        pass

    # Bedroom
    bedroom = None
    try:
        bedroom = float(tree.xpath(GET_INFO_XPATH_FOR_BEDROOM)[0].split(' ')[0])
    except Exception:
        bedroom = 0

    # Bathroom (float since bathroom can be .5)
    bathroom = None
    try:
        bathroom = float(tree.xpath(GET_INFO_XPATH_FOR_BATHROOM)[0].split(' ')[0])
    except Exception:
        bathroom = 0

    # Square feet
    size = None
    try:
        size = int(tree.xpath(GET_INFO_XPATH_FOR_SIZE)[0].split(' ')[0].replace(',', ''))
    except Exception:
        size = 0

    # Is for sale
    for_sale_text = str(tree.xpath(GET_INFO_XPATH_FOR_SALE))
    r = re.compile('.+For Sale.+')
    is_for_sale = len(filter(r.match, for_sale_text)) > 0

    # Listed price
    list_price = None
    try:
        list_price_raw = tree.xpath(GET_INFO_XPATH_LIST_FOR_PRICE)
        if len(list_price_raw) > 0:
            list_price = float(list_price_raw[0].replace(',', '').strip(' $'))
    except Exception:
        pass

    # geo
    latitude = None
    longitude = None
    try:
	longitude = html.tostring(tree.xpath(GET_INFO_XPATH_FOR_LATITUDE)[0])
	longitude = float(longitude.split('mlong":"')[1].split('"')[0])
	latitude = html.tostring(tree.xpath(GET_INFO_XPATH_FOR_LATITUDE)[0])
	latitude = float(latitude.split('mlat":"')[1].split('"')[0])
	
    except Exception:
        pass

    # Image
    image_url = None
    try:
        image_url = html.tostring(tree.xpath('''//img''')[1])
	image_url = image_url.split(' ')[2]
	image_url = image_url.split('"')[1]

    except Exception:
        pass 

    # Description
    description = None
    try:
        description = tree.xpath(GET_INFO_XPATH_DESCRIPTION)
    except Exception:
        pass

    # Basic facts
    facts = None
    try:
        facts = tree.xpath(GET_INFO_XPATH_FOR_FACTS)
    except Exception:
        pass

    # Additional facts
    additional_facts = None
    try:
        additional_facts = tree.xpath(GET_INFO_XPATH_FOR_ADDITIONAL_FACTS)
    except Exception:
        pass

    print({'zpid' : zpid})
    print({'street_address' : street_address})
    print({'city' : city})
    print({'state' : state})
    print({'zipcode' : zipcode})
    print({'property_type' : property_type})
    print({'bedroom' : bedroom})
    print({'bathroom' : bathroom})
    print({'size' : size})
    print({'latitude' : latitude})
    print({'longitude' : longitude})
    print({'is_for_sale' : is_for_sale})
    print({'list_price' : list_price})
    print({'image_url' : image_url})
    print({'description' : description})
    print({'facts' : facts})
    print({'additional_facts': additional_facts})

    return {'zpid' : zpid,
            'street_address' : street_address,
            'city' : city,
            'state' : state,
            'zipcode' : zipcode,
            'property_type' : property_type,
            'bedroom' : bedroom,
            'bathroom' : bathroom,
            'size' : size,
            'latitude' : latitude,
            'longitude' : longitude,
            'is_for_sale' : is_for_sale,
            'list_price' : list_price,
            'image_url' : image_url,
            'description' : description,
            'facts' : facts,
            'additional_facts' : additional_facts}

"""Get properties' information by zipcode"""
def get_properties_by_zip(zipcode):
    zpids = search_zillow_by_zip(zipcode)
    return [get_property_by_zpid(zpid) for zpid in zpids]

"""Get properties' information by city and state"""
def get_properties_by_city_state(city, state):
    zpids = search_zillow_by_city_state(city, state)
    return [get_property_by_zpid(zpid) for zpid in zpids]
