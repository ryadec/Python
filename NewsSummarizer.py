#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  6 15:55:06 2018

@author: ryandecosmo
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  6 00:14:15 2018

@author: ryandecosmo
"""

import requests
import re
import math
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from wordcloud import WordCloud


class WordCloudGenerator(object):
    	#A global list of stopwords borrowed from the nltk corpus for testing
    stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
				'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
				'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
				'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
				'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
				'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
				'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
				'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
				'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
				'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
				'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
				'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']
        
    def __init__(self, feed):
         self.feed = feed
         self.termFoundInDocumentID = {}
         self.documentTitles = {}
         self.documentList = []
    
    def __findArticlesFromFeed__(self,feed):
    		request = requests.get(feed)
    		soup = BeautifulSoup(request.content,features="xml" )
    		links = soup.findAll('link')
    		return links
    
    def __getDocuments__(self,documentList, links):
    		for link in links:
    			document = []
    			url = self.__removetags__(str(link))
    			print("crawling.. {}".format(url))
    			request = requests.get(url)
    			#html = request.text
    			soupHTML = BeautifulSoup(request.content, 'html.parser')
    			[document.append(htmlProp.get_text()) for htmlProp in soupHTML.find_all('p', {'itemprop': 'articleBody'})]
    			if len(document) > 0:
    				documentList.append(document)
    		return documentList
    
    def __getDescriptions__(self,items):
    		descriptions = []
    		for item in items:
    			descriptions.append(item.description)
    		return descriptions
    
    def __cleanDescriptions__(self,descriptions):
    		sentences = []
    		for d in descriptions:
    			sentence = self._removetags__(str(d))
    			sentences.append(sentence)
    			#print(sentence)
    		return sentences
    
    def __removetags__(self,html):
    	  cleanr = re.compile('<.*?>')
    	  cleantext = re.sub(cleanr, '', html)
    	  return cleantext
    
    
    def __createDocuments__(self,documentList, totalTermsDict):
    		regex = re.compile('[,-\.!?$\":\';@#]') #[^A-Za-z0-9]+') #
    		counter = 0
    		stopWordsOmitted = 0
    		documents = {}
    		for doc in documentList:
    			terms = {}
    			counter += 1
    			for t in doc:
    			   # t = t.lower() # we can use lowercase to increase accuracy a bit
    				#add the words to the document
    				for word in t.split():
    					word = regex.sub('', word)
    					if word not in self.stopwords:  
    						if word in terms:
    							terms[word] += 1
    						else:
    							terms[word] = 1
    						#create the document frequency and add which documents it appears
    						if word in totalTermsDict:
    							s = totalTermsDict[word]
    							s.add(counter)
    							totalTermsDict[word] = s
    						else:
    							totalTermsDict[word] = {counter}
    					else:
    						stopWordsOmitted += 1
    				documents[counter] = (terms) #,doc)
    		print("Stopwords omitted: {}".format(stopWordsOmitted))
    		return documents
    
    
    def __tfIDF__(self,documents, documentList):
    		weightedDocuments = {}
    		for doc in documents:
    			weightedTerms = {}
    			for term in documents[doc]:
    				weight = documents[doc].get(term) * math.log(len(self.documentList)/len(self.termFoundInDocumentID[term]))
    				weightedTerms[term] = weight
    			weightedDocuments[doc] = sorted(weightedTerms.items(), key=lambda x: x[1])#weightedTerms
    		return weightedDocuments
    
    
    def __getTopWords__(self,docs,numberOfWords):
    		topWordsList = []
    		for doc in docs:
    			#title = removetags(str(titles[doc+1]))
    			topWords = dict(sorted(docs[doc], key=lambda x: x[1], reverse=True)[:numberOfWords])
    			topWordsList.append(topWords)
    			#print("Doc#{} {} \n\n\n".format(doc,topWords))
    		return topWordsList
        
        
    def generateCloudFromFeed(self,topWordsPerArticle):
        links = self.__findArticlesFromFeed__(feed)
        self.__getDocuments__(self.documentList,links)
        documents = self.__createDocuments__(self.documentList,self.termFoundInDocumentID) #myLinks
        docs = self.__tfIDF__(documents, self.documentList)
        topWords = self.__getTopWords__(docs,topWordsPerArticle)
        return topWords




class WordCloudVisualizer(object):
    
    def __init__(self):
        pgf_with_rc_fonts = {"pgf.texsystem": "pdflatex"}
        plt.rcParams.update(pgf_with_rc_fonts)

        
    def display(self, wordCloudList):
        for cloud in wordCloudList:
            wcloud = WordCloud().generate_from_frequencies(cloud)
            plt.figure()
            plt.imshow(wcloud, interpolation="bilinear")
            plt.axis("off")
            plt.show()


"""
Driver Program to run the test
"""

feed = "https://abcnews.go.com/abcnews/topstories"

wc = WordCloudGenerator(feed)
words = wc.generateCloudFromFeed(30)

wv = WordCloudVisualizer()
wv.display(words)





        
        