import csv
import random as ran
import re
import webbrowser
from time import sleep

import requests
from flask import Flask, render_template, request
from selectorlib import Extractor

def scrape(url, e):
    # Create list of user agents
    user_agent_list = []
    with open('scrape/useragent.txt') as ulist:
        for each in ulist:
            user_agent_list.append(each)

    headers = {
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }
    headers['user-agent'] = ran.choice(user_agent_list).strip()
    # Download the page using requests
    # print("Downloading %s"%url)
    r = requests.get(url, headers=headers)
    # r = proxy.Proxy_Request(url=url, request_type=request_type)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n" % url, r.status_code)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d" % (url, r.status_code))
        return None
    # Pass the HTML of the page and create
    return e.extract(r.text)


def convert_url(url):
    asin_pattern = '[/]+[A-Z0-9]+[/?]'
    asin_number = re.search(asin_pattern, url)
    asin_number = asin_number.group()
    asin_number = asin_number[1:-1]
    url = "https://amazon.in/product-reviews/" + asin_number
    return url

def remove_rupee_symbol(x):
    rm = ['₹', ' ', ',']
    y = list(str(x))
    for i in y:
        if i in rm:
            y.remove(i)
    try:
        return int(float(''.join(y).strip()))
    except:
        return -1


def scrape_product(url,e):
    try:
        data = scrape(url,e)
        if data:
            # Brand
            try:
                str1 = data['Brand']
                if "Visit" in str1:
                    data['Brand'] = ' '.join(str1.split()[2:])
                elif "Brand:" in str1:
                    data['Brand'] = ' '.join(str1.split()[1:])
                else:
                    data['Brand'] = 'conditon not satisfied'
            except:
                data['Brand'] = -1

            # Price
            if data['Price'] == None:
                data['Price'] = ''
            else:
                data["Price"] = remove_rupee_symbol(data["Price"])

            # MRP
            if data["MRP"] == None:
                data['MRP'] = data['Price']
            else:
                data["MRP"] = remove_rupee_symbol(data["MRP"])
            # Return Policy
            try:
                if data['Return_Policy']:
                    data['Return_Policy'] = "yes"
                else:
                    data['Return_Policy'] = "no"
            except:
                data['Return_Policy'] = -1

            # Seller_URL
            try:
                if data["Seller_URL"]:
                    data["Seller_URL"] = 'https://www.amazon.in' + data['Seller_URL']
                else:
                    data["Seller_URL"] = "No Seller"
            except:
                data["Seller_URL"] = "No Seller"
                # Warranty
            try:
                if data['Warranty']:
                    data['Warranty'] = 'Yes'
                else:
                    data['Warranty'] = 'No'
            except:
                data['Warranty'] = -1

            # COD
            try:
                if data['COD']:
                    data['COD'] = 'Yes'
                else:
                    data['COD'] = 'No'
            except:
                data['COD'] = -1

            # Fullfiled_by_Amazon
            try:
                if data['Fullfiled_by_Amazon']:
                    data['Fullfiled_by_Amazon'] = 'Yes'
                else:
                    data['Fullfiled_by_Amazon'] = 'No'
            except:
                data['Fullfiled_by_Amazon'] = -1

            # All_Reviews_URL
            try:
                if data["All_Reviews_URL"]:
                    data["All_Reviews_URL"] = 'https://www.amazon.in' + data['All_Reviews_URL']
                else:
                    data["All_Reviews_URL"] = "No Reviews"
            except:
                data["All_Reviews_URL"] = "No Reviews"
            return (data)
    except TypeError as e:
        print('Type Error: ', e)
        return (data)


def scrape_review_data(url,e):
    try:
        data = scrape(url,e)
        if data:
            # Avg_rating
            try:
                if data['Avg_Rating']:
                    lst = data['Avg_Rating'].split()[:1]
                    data['Avg_Rating'] = ''.join(lst)
                else:
                    data['Avg_Rating'] = 'Not Available'
            except:
                data['Avg_Rating'] = -1

                # % Five star rating
            try:
                if data['five']:
                    data['five'] = data['five'][:-1]
                else:
                    data['five'] = '0'
            except:
                data['five'] = -1

            # % Four star rating
            try:
                if data['four']:
                    data['four'] = data['four'][:-1]
                else:
                    data['four'] = '0'
            except:
                data['four'] = -1

            # % Three star rating
            try:
                if data['three']:
                    data['three'] = data['three'][:-1]
                else:
                    data['three'] = '0'
            except:
                data['three'] = -1

            # % Two star rating
            try:
                if data['two']:
                    data['two'] = data['two'][:-1]
                else:
                    data['two'] = '0'
            except:
                data['two'] = -1

            # % One star rating
            try:
                if data['one']:
                    data['one'] = data['one'][:-1]
                else:
                    data['one'] = '0'
            except:
                data['one'] = -1

            return (data)
    except TypeError as e:
        print('Type Error: ', e)
        return (data)


def scrape_seller_data(url,e):
    try:

        data = scrape(url,e)
        if data:
            # Total_Rating
            try:
                if data['Total_Rating']:
                    rating = list(data['Total_Rating'])
                    while (',' in rating):
                        rating.remove(',')
                    data['Total_Rating'] = ''.join(rating)
                else:
                    data['Total_Rating'] = 'Not Available'
            except:
                data['Total_Rating'] = -1

            return (data)
    except TypeError as e:
        print('Type Error: ', e)
        return (data)


def scrape_main(url):
    print(url)
    with open('scrape/test.csv', 'w', encoding='utf-8', newline='') as outfile:
        # Writing headers in csv
        writer = csv.DictWriter(outfile,
                                fieldnames=["Product_Name", "Brand", "Category", "Sub_Category", "Price", "MRP",
                                            "Return_Policy", "Seller_URL", "Warranty", "COD", "Fullfiled_by_Amazon",
                                            "All_Reviews_URL", "Avg_Rating", "five", "four", "three", "two", "one",
                                            "rating_review", "Seller_Name", "Total_Rating", "Pect_Pos_Rating",
                                            "Pect_Neg_Rating", "Pect_Neu_Rating"], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        # Scraping

        sleep(ran.randint(1, 5))
        try:
            e = Extractor.from_yaml_file('scrape/Product.yml')
            d1 = scrape_product(url,e)
        except:
            print("Error:Please check product page")
        sleep(ran.randint(1, 5))
        try:
            e = Extractor.from_yaml_file('scrape/Review_Page.yml')
            d2 = scrape_review_data(d1['All_Reviews_URL'],e)
            d1.update(d2)
        except:
            print("Error:Please check reviews page")
        sleep(ran.randint(1, 5))
        try:
            e = Extractor.from_yaml_file('scrape/Seller_Page.yml')
            d3 = scrape_seller_data(d1['Seller_URL'],e)
            d1.update(d3)
        except:
            print("Error:Please check seller page")

        print(d1)
        writer.writerow(d1)
    outfile.close()
    webbrowser.open('scrape/test.csv', new=2)


app = Flask(__name__)

@app.route("/", methods =["GET", "POST"])
def start():
    if (request.method == "POST"):
        link = request.form.get("link")
        #webbrowser.open(link, new=2)
        scrape_main(link)
    return render_template('index.html')

app.run(debug=True)
