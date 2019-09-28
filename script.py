#jace
from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
from time import sleep
from urllib.request import Request
from urllib.request import urlopen

def get_html(url):
    
    html_content = ''
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'}) #hdr)
        html_page = urlopen(req).read()
        html_content = BeautifulSoup(html_page, "html.parser")
    except: 
        pass
        
    return html_content

def get_details(url):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp

    try:
        price = html.select('.productBasePrice')[0].get_text().strip()
        stamp['price'] = price.replace('C$', '').replace(',', '').strip()
    except: 
        stamp['price'] = None
        
    try:
        number = ''
        stock_items = html.select('#productDetailsList li')
        for stock_item in stock_items:
            stock_item_text = stock_item.get_text().strip()
            if 'in Stock' in stock_item_text:
                number = stock_item_text.replace('in Stock', '').strip()
        stamp['number'] = number
    except:
        stamp['number'] = None 
        
    try:
        title = html.select('#productName')[0].get_text().strip()
        stamp['title'] = title
    except:
        stamp['title'] = None      

    try:
        sub_category_cont = html.select('#categoryIcon')[0]
        sub_category = sub_category_cont.select('a')[0].get_text().strip()
        stamp['sub_category'] = sub_category
    except:
        stamp['sub_category'] = None        

    stamp['currency'] = "CAD"

    # image_urls should be a list
    images = []                    
    try:
        image_items = html.select('#productMainImage img')
        for image_item in image_items:
            img_src = image_item.get('src').replace('images/', 'images/large/').replace('.jpg', '_LRG.jpg')
            img = 'https://www.jacestamps.com/' + img_src
            if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
    
    try:
        raw_text = html.select('#productDescription')[0].get_text().strip()
        stamp['raw_text'] = raw_text
    except:
        stamp['raw_text'] = None
        
    if stamp['raw_text'] == None and stamp['title'] != None:
        stamp['raw_text'] = stamp['title']

    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('.itemTitle a'):
            item_link_temp = item.get('href').replace('&amp;', '&').strip()
            item_link_parts = item_link_temp.split('&zenid=')
            item_link = item_link_parts[0]
            if item_link not in items:
                items.append(item_link)
    except:
        pass

    try:
        next_item = html.select('li.pagination-next a')[0]
        if next_item:
            next_url = next_item.get('href').replace('&amp;', '&').strip()
    except:
        pass
    
    shuffle(list(set(items)))
    
    return items, next_url

def get_categories(category_url):
    
    items = []

    try:
        html = get_html(category_url)
    except:
        return items

    try:
        for item in html.select('.categoryListBoxContents a'):
            item_link = item.get('href')
            if item_link not in items:
                items.append(item_link)
    except: 
        pass

    shuffle(items)
    
    return items

def get_page_items_urls(url):
    page_items, page_url = get_page_items(url)
    for page_item in page_items:
        stamp = get_details(page_item)

item_dict = {
'Canada':'https://www.jacestamps.com/index.php?main_page=index&cPath=7&zenid=6fq7p13s0qdbbot8q1mphq85j6',
'Countries A-F':'https://www.jacestamps.com/index.php?main_page=index&cPath=1&zenid=6fq7p13s0qdbbot8q1mphq85j6',
'Countries G-0':'https://www.jacestamps.com/index.php?main_page=index&cPath=3',
'Countries P-Z':'https://www.jacestamps.com/index.php?main_page=index&cPath=5',
'$1 Deals':'https://www.jacestamps.com/index.php?main_page=index&cPath=8'
    }
    
for key in item_dict:
    print(key + ': ' + item_dict[key])   

selection = input('Choose category: ')
            
category_url = item_dict[selection]
categories = get_categories(category_url)
if categories:
    for category in categories:
        get_page_items_urls(category)
else:
    get_page_items_urls(category_url)