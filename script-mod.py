#jace
from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
from time import sleep
from urllib.request import Request
from urllib.request import urlopen
'''
from fake_useragent import UserAgent
import os
import sqlite3
from fake_useragent import UserAgent
import shutil
from stem import Signal
from stem.control import Controller
import socket
import socks
import requests

controller = Controller.from_port(port=9051)
controller.authenticate()

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9050)
    socket.socket = socks.socksocket

def renew_tor():
    controller.signal(Signal.NEWNYM)

def showmyip():
    url = "http://www.showmyip.gr/"
    r = requests.Session()
    page = r.get(url)
    soup = BeautifulSoup(page.content, "lxml")
    try:
    	ip_address = soup.find("span",{"class":"ip_address"}).text()
    	print(ip_address)
    except:
        print('IP problem')
    
UA = UserAgent(fallback='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2')
hdr = {'User-Agent': UA.random}
'''
hdr = {'User-Agent': 'Mozilla/5.0'}
def get_html(url):
    
    html_content = ''
    try:
        req = Request(url, headers= hdr)
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
        stamp['raw_text'] = raw_text.replace('"',"'")
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

def get_page_items_urls(page_url):
    count = 0
    while(page_url):
        page_items, page_url = get_page_items(page_url)
        for page_item in page_items:
            '''count += 1
            if count > randint(25,100):
                print('Sleeping...')
                sleep(randint(500,2000))
                renew_tor()
                connectTor()
                hdr['User-Agent']=UA.random
                count = 0
            else:
                pass'''
            stamp = get_details(page_item)
            if stamp['raw_text'] == None and stamp['price']==None:
                continue
            '''next_step = query_for_previous(stamp)
            if next_step == 'continue':
                print('Only updating price')
                continue
            elif next_step == 'pass':
                print('Inserting the item')
                pass
            else:
                break
            db_update_image_download(stamp)

def file_names(stamp):
    file_name = []
    rand_string = "RAND_"+str(randint(0,10000000))
    file_name = [rand_string+"-" + str(i) + ".png" for i in range(len(stamp['image_urls']))]
    return(file_name)

def query_for_previous(stamp):
    # CHECKING IF Stamp IN DB
    os.chdir("/Volumes/Stamps/")
    conn1 = sqlite3.connect('Reference_data.db')
    c = conn1.cursor()
    col_nm = 'url'
    col_nm2 = 'raw_text'
    unique = stamp['url']
    unique2 = stamp['raw_text']
    c.execute('SELECT * FROM jacestamps WHERE {cn} LIKE "{un}%" AND {cn2} LIKE "{un2}%"'.format(cn=col_nm, cn2=col_nm2, un=unique, un2=unique2))
    all_rows = c.fetchall()
    c.close()
    price_update=[]
    price_update.append((stamp['url'],
    stamp['raw_text'],
    stamp['scrape_date'], 
    stamp['price'], 
    stamp['currency'],
    stamp['number']))
    
    if len(all_rows) > 0:
        print ("This is in the database already")
        conn1 = sqlite3.connect('Reference_data.db')
        c = conn1.cursor()
        c.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency, number) VALUES(?,?,?,?,?,?)""", price_update)
        try:
            c.commit()
            c.close()
        except:
            sleep(.77)
            c.commit()
            c.close()        
        print (" ")
        #url_count(count)
        sleep(randint(10,45))
        next_step = 'continue'
    else:
        os.chdir("/Volumes/Stamps/")
        conn2 = sqlite3.connect('Reference_data.db')
        c2 = conn2.cursor()
        c2.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency, number) VALUES(?,?,?,?,?,?)""", price_update)
        try:
            c2.commit()
            c2.close()
        except:
            sleep(.77)
            c2.commit()
            c2.close()        
        next_step = 'pass'
    print("Price Updated")
    return(next_step)

def db_update_image_download(stamp): 
    req = requests.Session()
    directory = "/Volumes/Stamps/stamps/jacestamps/" + str(datetime.datetime.today().strftime('%Y-%m-%d')) +"/"
    image_paths = []
    names = file_names(stamp)
    image_paths = [directory + names[i] for i in range(len(names))]
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    for item in range(0,len(names)):
        print (stamp['image_urls'][item])
        try:
            imgRequest1=req.get(stamp['image_urls'][item],headers=hdr, timeout=60, stream=True)
        except:
            print ("waiting...")
            sleep(randint(3000,6000))
            print ("...")
            imgRequest1=req.get(stamp['image_urls'][item], headers=hdr, timeout=60, stream=True)
        if imgRequest1.status_code==200:
            with open(names[item],'wb') as localFile:
                imgRequest1.raw.decode_content = True
                shutil.copyfileobj(imgRequest1.raw, localFile)
                sleep(randint(18,30))
    stamp['image_paths']=", ".join(image_paths)
    #url_count += len(image_paths)
    database_update =[]

    # PUTTING NEW STAMPS IN DB
    database_update.append((
        stamp['url'],
        stamp['raw_text'],
        stamp['title'],
        stamp['sub_category'],
        stamp['scrape_date'],
        stamp['image_paths']))
    os.chdir("/Volumes/Stamps/")
    conn = sqlite3.connect('Reference_data.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.executemany("""INSERT INTO jacestamps ('url','raw_text', 'title', 'category',
    'scrape_date','image1_path') 
    VALUES (?, ?, ?, ?, ?, ?)""", database_update)
    try:
        cur.commit()
        cur.close()
    except:
        sleep(.77)
        cur.commit()
        cur.close()
    print ("all updated")
    print ("++++++++++++")
    print (" ")
    sleep(randint(45,140)) 
'''
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