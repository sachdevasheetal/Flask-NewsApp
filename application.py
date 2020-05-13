from flask import Flask, render_template, abort, jsonify, request, redirect, url_for


from newsapi import NewsApiClient

from collections import Counter

import sys, os, string

from datetime import datetime


import collections

application = Flask(__name__)
newsapi = NewsApiClient(api_key='') #Enter your  Google News API Key
@application.route("/get_source", methods=['POST','GET'])
def get_source():
    if request.method == 'GET':
        val=str(request.args.get('input'))
        print(val)
        if val=="all":
                sources = newsapi.get_sources(language='en',
                                          country='us')
        else :
                sources = newsapi.get_sources(category=val,language='en',
                                          country='us')
        return jsonify(sources)



@application.route("/get_form_response", methods=['POST','GET'])
def get_form_response():
   if request.method == 'GET':
       keyword=str(request.args.get('keyword'))
       source=str(request.args.get('source'))
       source=source.lower().replace(' ', '-')
       # category=request.args.get('category')
       from_date=str(request.args.get('from_date'))
       from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
       to_date=str(request.args.get('to_date'))
       to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
       print(keyword)

       print('sheetal')
       dict_obj = dict()
       try:
            if(source=='all'):
                sources = newsapi.get_everything(q=keyword, from_param=from_date_obj, to=to_date_obj, language='en', sort_by='relevancy', page_size=30)
            else:
                sources = newsapi.get_everything(q=keyword, sources=source, from_param=from_date_obj, to=to_date_obj, language='en', sort_by='relevancy', page_size=30)

            # dict_obj.add('word', word.capitalize())
            dict_obj['status']=sources['status']
            print(sources)
            if 'message' in sources:
                dict_obj['message']=sources['message']
            all_articles=[]
            if 'articles' in sources:
                for i in range(len(sources['articles'])):
                    dict_obj_articles = dict()
                    if len(all_articles)<10:
                        if 'articles' in sources and 'source' in sources['articles'][i] and 'author' in sources['articles'][i] and 'description' in sources['articles'][i] and 'title' in sources['articles'][i] and 'url' in sources['articles'][i] and 'urlToImage' in sources['articles'][i] and 'publishedAt' in sources['articles'][i] and 'id' in sources['articles'][i]['source'] and 'name'in sources['articles'][i]['source']:
                            if sources['articles'][i]['source'] and sources['articles'][i]['author'] and sources['articles'][i]['description'] and  sources['articles'][i]['title'] and sources['articles'][i]['url'] and sources['articles'][i]['urlToImage'] and sources['articles'][i]['publishedAt'] and sources['articles'][i]['source']['id'] and sources['articles'][i]['source']['name']:
                                dict_obj_source = dict()
                                dict_obj_source['id']=sources['articles'][i]['source']['id']
                                dict_obj_source['name']=sources['articles'][i]['source']['name']
                                dict_obj_articles['source']=dict_obj_source
                                dict_obj_articles['author']=sources['articles'][i]['author']
                                d1 = datetime.strptime(sources['articles'][i]['publishedAt'],"%Y-%m-%dT%H:%M:%SZ")
                                d2=d1.strftime('%m/%d/%Y')
                                dict_obj_articles['publishedAt']=d2
                                dict_obj_articles['description']=sources['articles'][i]['description']
                                dict_obj_articles['title']=sources['articles'][i]['title']
                                dict_obj_articles['url']=sources['articles'][i]['url']
                                dict_obj_articles['urlToImage']=sources['articles'][i]['urlToImage']
                                all_articles.append(dict_obj_articles)
                                dict_obj['articles']=all_articles
                    else:
                        break

       except Exception as ex:
            js=eval(str(ex))
            dict_obj['status']=js['status']
            dict_obj['message']=js['message']

       return jsonify(dict_obj)

@application.route("/wordcloud", methods=['POST','GET'])
def wordcloud():
    if request.method == 'GET':
        words = newsapi.get_top_headlines(page_size=30,language='en')
        str_list = ''
        for i in range(len(words['articles'])):
            str_list=str_list+words['articles'][i]['title']+' '
        exclude = set(string.punctuation)
        exclude.remove('\'')
        print (exclude)
        str_list = ''.join(ch for ch in str_list if ch not in exclude)
        split_it = str_list.split()
        counter = Counter(split_it)
        most_occur = counter.most_common(50)
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, 'static', 'stopwords_en.txt')
        stopwords = set(line.strip() for line in open(json_url))
        wordcount = {}
# To eliminate duplicates, remember to split by punctuation, and use case demiliters.
        for word in str_list.lower().split():
            word = word.replace(".","")
            word = word.replace(",","")
            word = word.replace(":","")
            word = word.replace("\"","")
            word = word.replace("!","")
            word = word.replace("–","")
            word = word.replace("\'","")
            word = word.replace("*","")
            word = word.replace("|","")
            if word not in stopwords:
                if word not in wordcount :
                    wordcount[word] = 1
                else:
                    wordcount[word] += 1
        word_counter = collections.Counter(wordcount)
        ret = []
        val=18
        prev=-1
        for word, count in word_counter.most_common(30):
            print(word, ": ", count)
            dict_obj = dict()
            dict_obj['word']=word.capitalize()
            if prev==-1 or prev==count:
                dict_obj['size']=val
            else:
                dict_obj['size']=val-1
                val=val-0.5
            prev=count
            ret.append(dict_obj)
        return jsonify(obj=ret)

@application.route("/get_cnn", methods=['POST','GET'])
def get_cnn():
    if request.method == 'GET':
        cnn = newsapi.get_top_headlines(sources='cnn',language='en',page_size=30)
        dict_obj = dict()
        dict_obj['status']=cnn['status']
        print(cnn.keys())
        if 'message' in cnn:
            dict_obj['message']=cnn['message']
        all_articles=[]
        for i in range(len(cnn['articles'])):
            dict_obj_articles = dict()
            if len(all_articles)<4:
                if 'source' in cnn['articles'][i] and 'author' in cnn['articles'][i] and 'description' in cnn['articles'][i] and 'title' in cnn['articles'][i] and 'url' in cnn['articles'][i] and 'urlToImage' in cnn['articles'][i] and 'publishedAt' in cnn['articles'][i] and 'id' in cnn['articles'][i]['source'] and 'name'in cnn['articles'][i]['source']:
                    if cnn['articles'][i]['source'] and cnn['articles'][i]['author'] and cnn['articles'][i]['description'] and  cnn['articles'][i]['title'] and cnn['articles'][i]['url'] and cnn['articles'][i]['urlToImage'] and cnn['articles'][i]['publishedAt'] and cnn['articles'][i]['source']['id'] and cnn['articles'][i]['source']['name']:
                        dict_obj_source = dict()
                        dict_obj_source['id']=cnn['articles'][i]['source']['id']
                        dict_obj_source['name']=cnn['articles'][i]['source']['name']
                        dict_obj_articles['source']=dict_obj_source
                        dict_obj_articles['author']=cnn['articles'][i]['author']
                        dict_obj_articles['publishedAt']=cnn['articles'][i]['publishedAt']
                        dict_obj_articles['description']=cnn['articles'][i]['description']
                        dict_obj_articles['title']=cnn['articles'][i]['title']
                        dict_obj_articles['url']=cnn['articles'][i]['url']
                        dict_obj_articles['urlToImage']=cnn['articles'][i]['urlToImage']
                        all_articles.append(dict_obj_articles)

                        dict_obj['articles']=all_articles
            else:
                break
        print(len(dict_obj['articles']))
        return jsonify(dict_obj)

@application.route("/get_fox", methods=['POST','GET'])
def get_fox():
    if request.method == 'GET':
        fox = newsapi.get_top_headlines(sources='fox-news',language='en',page_size=30)
        dict_obj = dict()
        dict_obj['status']=fox['status']
        print(fox.keys())
        if 'message' in fox:
            dict_obj['message']=fox['message']
        all_articles=[]
        for i in range(len(fox['articles'])):
            dict_obj_articles = dict()
            if len(all_articles)<4:
                if 'source' in fox['articles'][i] and 'author' in fox['articles'][i] and 'description' in fox['articles'][i] and 'title' in fox['articles'][i] and 'url' in fox['articles'][i] and 'urlToImage' in fox['articles'][i] and 'publishedAt' in fox['articles'][i] and 'id' in fox['articles'][i]['source'] and 'name'in fox['articles'][i]['source']:
                    if fox['articles'][i]['source'] and fox['articles'][i]['author'] and fox['articles'][i]['description'] and  fox['articles'][i]['title'] and fox['articles'][i]['url'] and fox['articles'][i]['urlToImage'] and fox['articles'][i]['publishedAt'] and fox['articles'][i]['source']['id'] and fox['articles'][i]['source']['name']:
                        dict_obj_source = dict()
                        dict_obj_source['id']=fox['articles'][i]['source']['id']
                        dict_obj_source['name']=fox['articles'][i]['source']['name']
                        dict_obj_articles['source']=dict_obj_source
                        dict_obj_articles['author']=fox['articles'][i]['author']
                        dict_obj_articles['publishedAt']=fox['articles'][i]['publishedAt']
                        dict_obj_articles['description']=fox['articles'][i]['description']
                        dict_obj_articles['title']=fox['articles'][i]['title']
                        dict_obj_articles['url']=fox['articles'][i]['url']
                        dict_obj_articles['urlToImage']=fox['articles'][i]['urlToImage']
                        all_articles.append(dict_obj_articles)

                        dict_obj['articles']=all_articles
            else:
                break
        print(len(dict_obj['articles']))

        return jsonify(dict_obj)

@application.route("/get_all", methods=['POST','GET'])
def get_all():
    if request.method == 'GET':
        all = newsapi.get_top_headlines(language='en')
        dict_obj = dict()
        dict_obj['status']=all['status']
        print(all.keys())
        if 'message' in all:
            dict_obj['message']=all['message']
        all_articles=[]
        for i in range(len(all['articles'])):
            dict_obj_articles = dict()
            if len(all_articles)<5:
                if 'source' in all['articles'][i] and 'author' in all['articles'][i] and 'description' in all['articles'][i] and 'title' in all['articles'][i] and 'url' in all['articles'][i] and 'urlToImage' in all['articles'][i] and 'publishedAt' in all['articles'][i] and 'id' in all['articles'][i]['source'] and 'name'in all['articles'][i]['source']:
                    if all['articles'][i]['source'] and all['articles'][i]['author'] and all['articles'][i]['description'] and  all['articles'][i]['title'] and all['articles'][i]['url'] and all['articles'][i]['urlToImage'] and all['articles'][i]['publishedAt'] and all['articles'][i]['source']['id'] and all['articles'][i]['source']['name']:
                        dict_obj_source = dict()
                        dict_obj_source['id']=all['articles'][i]['source']['id']
                        dict_obj_source['name']=all['articles'][i]['source']['name']
                        dict_obj_articles['source']=dict_obj_source
                        dict_obj_articles['author']=all['articles'][i]['author']
                        dict_obj_articles['publishedAt']=all['articles'][i]['publishedAt']
                        dict_obj_articles['description']=all['articles'][i]['description']
                        dict_obj_articles['title']=all['articles'][i]['title']
                        dict_obj_articles['url']=all['articles'][i]['url']
                        dict_obj_articles['urlToImage']=all['articles'][i]['urlToImage']
                        all_articles.append(dict_obj_articles)

                        dict_obj['articles']=all_articles
            else:
                break
        print(len(dict_obj['articles']))
        return jsonify(dict_obj)

@application.route("/")
def search():
    return application.send_static_file("search.html")

if __name__ == "__main__":
    application.debug = True
    application.run()
