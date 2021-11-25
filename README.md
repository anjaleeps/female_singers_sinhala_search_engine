# Female Singers Sinhala Search Engine
In this repository, the code for a female singers search engine operating in Sinhala language is provided. The system is built using Python, Elasticsearch, Flask, and Javascript technologies.

## Overview
The system accepts a sinhala language search queries through a web interface and query the female singer data indexed on Elasticsearch to retrieve and return singer data related to the query. The indexed data stores 10 different fields of data as indicated in the following list. 
<ul>
  <li>Name</li>
  <li>Personal information</li>
  <li>Career information</li>
  <li>Discography</li>
  <li>Awards</li>
  <li>Summary</li>
  <li>Birthday</li>
  <li>Active period</li>
  <li>Genre</li>
  <li>Url to related Wikipedia page</li>
</ul>

## Scraping data
The singer data were scraped from Wikipedia using the [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page) and a NPM module named [wtf_wikipedia](https://www.npmjs.com/package/wtf_wikipedia). The latter module handled retrieving data under different sections and cleaning unnecessary components such as links, references from the text. Once singer data is scraped, the texts are translated into Sinhala language using the [Google Translate library](https://www.npmjs.com/package/@google-cloud/translate) provided by Google cloud. The ```data_collector.js``` file contains the related scraper code and ```data_original.csv``` and ```data_preprocessed.json``` contain the original and preprocessed data respectively.

## Processing search query
The sinhala language search query submitted through the web interface are processed by ```query_processor.py``` to retrive the matching results from the indexed elasticsearxh database. The query first goes through an initial preprocessing step to remove stop words and punctuation. Thr next intent classification step that divides all queries into two possible types. They are:
<ul>
  <li>Exact phrase search queries. ex: ග්‍රැමී දිනා ඇත</li> 
  <li>Multi match search queries ex: එමිලි බාර්කර්ගේ ප්‍රසිද්ධ ගීත, ඇඩෙල්ගේ දරුවාගේ නම කුමක්ද?</li> 

Finally, Elasticsearch DSL queries are executed to retrive documents belonging to the relavant type of query from the database. 
