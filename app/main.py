from flask import Flask, render_template, redirect, url_for, request
import urllib.request, urllib.parse, urllib.error, json, requests, wikipedia
from bs4 import BeautifulSoup


app = Flask(__name__,static_url_path='/static')

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/test/', methods=['GET', 'POST'])
def test():
    return render_template("test.html")

@app.route('/samp')
def samp():
    data = {
        "brand" : "Ford",
        "model" : "mustang",
        "year" : 1994,
    }
    return render_template('samp.html',data = data)

@app.route('/search', methods=['GET', 'POST']) 
def search(): 
    string=request.form.get('srch-term') 
    inurl = 'http://127.0.0.1:8983/solr/BM25/select?indent=on&indent=on&q=' + urllib.request.pathname2url( 
        string) + '&rows=10' + '&wt=json' 
    urlData = urllib.request.urlopen(inurl) 
    docs = json.load(urlData)['response']['docs'] 
    data=[] 
    data.append(string) 
    wikidata = wikipedia.page(string) 
    wrds = wikidata.content.split(" ") 
    data.append(" ".join(wrds[:70])) 
    data.append("https://en.wikipedia.org/wiki/"+string) 
    i=0 
    for doc in docs: 
        dataMap={} 
        dataList=[] 
        #lang=getLanguage() 
        lang='en' 
        text=doc['text_en'][0] 
        dataList.append(doc['id'])  #0 -- id 
        dataList.append("username") #1 -- username 
        dataList.append('06-29')  #2 -- date 
        dataList.append(text)   #3 -- text 
        dataMap[i]=dataList 
        data.append(dataMap) 
        i+=1 
    return render_template('resultsPage.html', data=data)

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATE_AUTO_RELOAD'] = True
    app.run(debug=True)

