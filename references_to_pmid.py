# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 19:50:34 2022

@author: Pablo
"""
import requests
import pycountry
import numpy as np
import pandas as pd
from time import sleep
import xmltodict as xml2dict
from matplotlib import pyplot as plt


PMID = '20064380' # by Klumpp S, Zhang Z, and Hwa T.
YOUR_EMAIL = 'youremail@gmail.com'
TOOL = ''
DELAY = 1/3 # in seconds

URL_ELINK = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi'
URL_ESUMM = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
URL_EFETCH= 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'

PARAMS_ARTICLE = {
    'dbfrom' : 'pubmed',
    'linkname' : 'pubmed_pubmed_citedin',
    'id' : PMID,
    'retmode' : 'json'
    }

PARAMS_AUTHOR = {
    'db' : 'pubmed',
    'retmode' : 'xml'
    }

def author_to_fullname(author_dict):
    return author_dict['LastName']+', '+author_dict['ForeName']


def author_to_affiliation(author_dict):
    try:
        return author_dict['AffiliationInfo']['Affiliation']
    except: 
        return None

def affiliation_to_country(affiliation, countries, error_val=None):
    try:
        return [c for c in countries if c in affiliation][0]
    except:
        return error_val

def article_to_authors(article):
    auth_list = article['MedlineCitation']['Article']['AuthorList']['Author']
    
    # First check if article was written by a single author
    if type( auth_list ) == dict:
        return [ auth_list , ]
    
    #... if not, loop over all authors in the list
    elif type( auth_list)== list:    
        return auth_list
    
def article_to_title(article):
    return  article['MedlineCitation']['Article']['ArticleTitle'] 
    
def article_to_pubyear(article, error_val=None):
    try:
        date = article['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']
        return int( date['Year'] )
    except:
        return error_val

def get_countries():
    cnt = list( pycountry.countries)
    countries = []
    for country in cnt:
        try:
            # countries.append( country.official_name )
            countries.append( country.name )
        except:
            countries.append( country.name )
    return countries

def article_to_pmid(article):
    return article['MedlineCitation']['PMID']['#text']

def article_to_journal(article):
    return article['MedlineCitation']['Article']['Journal']['Title']


# Find title of original queried paper
_params = PARAMS_AUTHOR.copy()
_params.update( {'id' : PMID })
_params.update( {'retmode' : 'json' })
response = requests.get( URL_ESUMM, params = _params, timeout = 3)
json = response.json()
#...
title = json['result'][PMID]['title']
author_first = json['result'][PMID]['authors'][0]['name']
author_last = json['result'][PMID]['authors'][-1]['name']
print('%s by:' % title )
_ = [print('  ·%s' % author['name'] ) for author in json['result'][PMID]['authors'] ];

# Find number of citations of pubmed entry
response =requests.get(URL_ELINK, params=PARAMS_ARTICLE, timeout=3)
json = response.json()
#...
cited_by = json['linksets'][0]['linksetdbs'][0]['links']
print('Cited by a total of %d other articles.' % len(cited_by))

# Retrieve dataframe
df = pd.DataFrame( columns=[
    'Author','Affiliation','Country','PMID','Title','Journal', 'Year'
    ]
    )

countries = get_countries()
retstart = 0
retmax = 100

while retstart < len( cited_by ):
    
    # Update query parameters
    _params = PARAMS_AUTHOR.copy()
    _params.update( {'id' : ','.join(cited_by[retstart:(retstart+retmax)]) })
    
    # GET request to EFetch
    response = requests.get( URL_EFETCH, params = _params, timeout = 3)
    
    # Check response status, exit if error
    if response.status_code != 200:
        print('Error in the GET request, status code: %d' % response.status_code)
        print('Length of URI: %d' % len(response.request.url))
        break
    
    # Convert response XML to dictionnary to easily navigate data
    response_dict = xml2dict.parse( response.text )    
    num_articles = len(response_dict['PubmedArticleSet']['PubmedArticle'])
    print('Successful GET request with records from %d to %d' %
           (retstart, retstart+num_articles-1) 
         )
        
    # Parse article object to export valuable information
    for article in response_dict['PubmedArticleSet']['PubmedArticle']:
        title    = article_to_title(   article ) 
        year     = article_to_pubyear( article ) 
        pmid     = article_to_pmid(    article )
        journal  = article_to_journal( article )
        _authors = article_to_authors( article )
        
        for author in _authors:
            author_name   = author_to_fullname( author )
            author_affil  = author_to_affiliation( author ) 
            affil_country = affiliation_to_country(author_affil, countries, error_val='')
            
            # Append new element to DataFrame
            element = [
                author_name,
                author_affil,
                affil_country,
                pmid,
                title,
                journal,
                year
                ]
            df.loc[len(df.index)] = element
        
    retstart += retmax
    sleep(DELAY)

    
print('Finished!')   


# Compute the number of people that has cited the article
unique_authors = np.unique(df['Author'])
print('Number of unique authors: %d' % len(unique_authors) )


# Compute the number of citations from each author
num_citations = np.array([ len( df[ df['Author']==author]) for author in unique_authors ])
print('Most citing author %s with %d citations.' % (unique_authors[num_citations.argmax()], num_citations.max()) )

# Show the most citing authors
idx = np.nonzero( num_citations>2 )[0]

plt.figure( figsize=(5,10), dpi=300)
plt.barh( range(len(idx)), num_citations[idx] )
plt.yticks( ticks=range(len(idx)), labels=unique_authors[idx])
plt.gca().invert_yaxis()
plt.grid()
plt.title(title)

plt.tight_layout()


# Show authors with their affiliation in a given country:
country = 'Spain'
_=[ print(x) for x in np.unique( df[ df['Country']==country]['Author'] ) ];    
    
    
    