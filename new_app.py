from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://vickydharmwan:$vkkymongo2005V@cluster0.i8ywlla.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db=client['review_scrap']

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.find_all("div", {"class": "cPHDOP col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            #print(productLink)
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            #print(prod_html)
            #comment_box = prod_html.find_all('div', {'class': "cPHDOP col-12-12"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            driver = webdriver.Chrome()
            driver.get(productLink)
            time.sleep(3)
            soup = bs(driver.page_source, 'html.parser')


            names=[]
            comment_heads=[]
            ratings=[]
            comments=[]
            # 2. Find your containers as before
            comment_box = soup.find_all("div", {"class":"cPHDOP col-12-12"})
            print(len(comment_box))

            # 3. For each comment_box, search for review paragraphs

            for i in comment_box:
                name = i.find_all('p', class_="_2NsDsF AwS1CA")
                if name:
                    names.append(name)
                commentHead = i.find_all('p', class_="z9E0IG")
                if commentHead:
                    comment_heads.append(commentHead)
                rating = i.find_all('div', class_="XQDdHH Ga3i8K")
                if rating:
                    ratings.append(rating)
                custComment = i.find_all('div', class_="ZmyHeo")
                if custComment:
                    comments.append(custComment)
            name_tag=[]
            comment_head_tag=[]
            rating_tag=[]
            comment_tag=[]
            a=len(names)
            for i in range(a):
                if comment_box:
                    name_tag = [tag.get_text(strip=True) for tag in names[0]]
                    comment_head_tag = [tag.get_text(strip=True) for tag in comment_heads[0]]
                    rating_tag = [tag.get_text(strip=True) for tag in ratings[0]]
                    comment_tag = [tag.get_text(strip=True) for tag in comments[0]]
                    #print(name_tag)
                    #print(comment_head_tag)
                    #print(rating_tag)
                    #print(comment_tag)
            b=len(name_tag)
            print(b)
            for i in range(b):
                if name_tag[i] or rating_tag[i] or comment_head_tag[i] or comment_tag[i]:
                    mydict = {
                            "Product": searchString,
                            "Name": name_tag[i],
                            "Rating": rating_tag[i],
                            "CommentHead": comment_head_tag[i],
                            "Comment": comment_tag[i]
                        }
                print(mydict)
                review_col=db['review_scrap_data']
                review_col.insert_one(mydict)
                reviews.append(mydict)
            driver.quit()
    logging.info("log my final result {}".format(reviews))
    return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
                    

            



if __name__=="__main__":
    app.run(host="0.0.0.0")
