from flask import Flask, render_template, redirect, url_for, request
import urllib,json,requests,wikipedia
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("test.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    string=request.form.get('srch-term')
    print string
    #string="syria"
    inurl = 'http://localhost:8983/solr/BM25/select?indent=on&indent=on&q=' + urllib.pathname2url(
        string) + '&rows=10' + '&wt=json'
    print inurl
    data = urllib.urlopen(inurl)
    docs = json.load(data)['response']['docs']
    result='';
    with open('start.txt') as f:
        for row in f:
            result+=row
    result+=' placeholder=\''
    result+=string
    result+='\'> <input type="submit" id="button" onclick="myFunction(0)"> </form><br> <br> <br>'
    i=0
    result+="<div style=\"float:left; width:30%;\"> <a href='https://en.wikipedia.org/wiki/"+string+"'><h3>"+string.title()+"</h3></a>"
    wikidata = wikipedia.page(string)
    wrds=wikidata.content.split(" ")
    result+=" ".join(wrds[:70])
    result+="...<a href='https://en.wikipedia.org/wiki/"+string+"'>Wikipedia</a></div> <div style=\"float:right; width:70%; \">"
    for doc in docs:
        if 'text_en' in doc:
            #resp = requests.get(doc['tweet_urls'][0])
            if 1==1:
                result+="<div id="+str(i)+"> <b>"
                result+="<a style=\"margin-left:5em;margin-left:5em\" color:blue\" href=\'"
                result+='https://twitter.com/Wonam6/status/'
                result+=doc['id']
                result+="\'>"+doc['text_en'][0]
                '''words=doc['text_en'][0].split(":")
                if len(words)>1:
                    result += words[1].split("#")[0]
                else:
                    result += words[0]'''

                result += '</a></b><br>'
                #result += "<a style=\"margin-left:5em;margin-left:5em\" href=\'https://twitter.com/Wonam6/status/"+doc['id']+"\'>"
                #result += 'https://twitter.com/Wonam6/status/'+doc['id']+'</a><br>'
                result += '<p style=\'width:550px;margin-left:5em;margin-left:5em\'>'
                '''soup = BeautifulSoup(resp.text, 'html.parser')
                l = soup.findAll("p")
                if l!=None and len(l)>=1:
                    result+= l[0].text
                else:
                    result+=doc['text_en'][0]'''
                result+=doc['text_en'][0]
                result+="...</p>"
                result+='</div><br><br><br>'
                i+=1
    result+="</div>"
    #print result
    with open('end.txt') as f:
        for row in f:
            result+=row
    return result
    #return render_template("resultsPage.html")
    #return redirect(url_for('resultsPage'))

if __name__ == '__main__':

    app.run(debug=True)