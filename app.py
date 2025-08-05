from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
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
            commentboxes = prod_html.find_all('div', {'class': "cPHDOP col-12-12"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            driver = webdriver.Chrome()
            driver.get(productLink)
            time.sleep(3)
            soup = bs(driver.page_source, 'html.parser')

                    # 2. Find your containers as before
            comment_box = soup.find_all("div", {"class":"cPHDOP col-12-12"})
            
            #for commentbox in commentboxes:
            for i in comment_box:  
                try:
                       name_elem = i.find('p', class_="_2NsDsF AwS1CA")
                       print(name_elem)
                       name = name_elem.text.strip() if name_elem else "No Name"
                       print(name)
                        #name.encode(encoding='utf-8')
                        #name = commentbox.div.div.find_all('p', {'_2NsDsF AwS1CA'})[0].text

                        # 3. For each comment_box, search for review paragraphs
                       # for i in comment_box:
                       
                            #name_0= i.find_all('p', class_="_2NsDsF AwS1CA")
                            # name=i.find_all('p', class_="_2NsDsF AwS1CA")
                            #name.text.strip()
                            #for p in name:
                               # print(p.text)

                except:
                        logging.info("name")

                try:
                       rating_elem = i.find('div', class_="XQDdHH Ga3i8K")
                       rating = rating_elem.text.strip() if rating_elem else "No Rating"
                       print(rating)
                        #rating.encode(encoding='utf-8')
                        #rating = commentbox.div.div.div.div.text
                        # 3. For each comment_box, search for review paragraphs
                        #for i in comment_box:
                       
                            #rating_0= i.find_all('div', class_="XQDdHH Ga3i8K")
                            #rating=i.find_all('div', class_="XQDdHH Ga3i8K")
                            #rating.text.strip()
                            #for s in rating:
                                #print(s.text)

                        


                except:
                        rating = 'No Rating'
                        logging.info("rating")

                try:
                      commentHead_elem = i.find('p', class_="z9E0IG")
                      commentHead = commentHead_elem.text.strip() if commentHead_elem else "No Heading"
                      print(commentHead)
                        #commentHead.encode(encoding='utf-8')
                        #commentHead = commentbox.div.div.div.p.text
                        #for i in comment_box:
                        
                            #commentHead_0= i.find_all('p', class_="z9E0IG")
                        #commentHead=i.find_all('p', class_="z9E0IG")
                            #commentHead.text.strip()
                            #for p in commentHead:
                               # print(p.text)

                except:
                        commentHead = 'No Comment Heading'
                        logging.info(commentHead)
                try:
                        custComment_elem = i.find('div', class_="ZmyHeo")
                        custComment = custComment_elem.text.strip() if custComment_elem else "No Comment"
                        print(custComment)
                        #comtag = commentbox.div.div.find_all('div', {'class': ''})
                        #custComment.encode(encoding='utf-8')
                        #custComment = comtag[0].div.
                        #for i in comment_box:
                         
                            #custComment= i.find_all('div', class_="ZmyHeo")
                            #custComment=i.find_all('div', class_="ZmyHeo")
                            #print(custComment.text.strip())
                            #for c in custComment:
                                #print(c.text)
                except Exception as e:
                        logging.info(e)
                driver.quit()
                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                            "Comment": custComment}
                print(mydict)
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
                logging.info(e)
                return 'something is wrong'
        # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
