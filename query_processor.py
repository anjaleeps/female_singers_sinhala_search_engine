from elasticsearch import Elasticsearch
from googletrans import Translator
from nltk import word_tokenize
from nltk.corpus import stopwords
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from elastic_config import Config

personalInfo_kw = ['personalInfo', 'personal', 'life', 'biography', 'childhood', 'relationship', 'family']
career_kw = ['careerInfo', 'career', 'job', 'profession', 'work']
discography_kw = ['discography', 'song', 'album', 'single', 'sing', 'play']
awards_kw = ['award', 'nomination', 'accolades', 'win', 'nominate', 'recognition']
summary_kw = ['summary', 'info']
birthdate_kw = ['birthDate', 'birthday', 'birth', 'born', 'age', 'old']
years_active_kw = ['yearsActive', 'active','period', 'era']
genre_kw = ['genre', 'style', 'music']
fields = [personalInfo_kw, career_kw, discography_kw, awards_kw, summary_kw, birthdate_kw, years_active_kw, genre_kw]

elasticsearch = Elasticsearch([{'host': Config.host.value, 'port': Config.port.value}])


def search_query(query):
    query_en = translate_to_english(query)
    print(query_en)
    query_type, relavant_fields, search_query = find_query_type(query_en)
    results = None
    if (query_type == 0):
        results = get_multi_match_results(search_query)
    elif (query_type == 1):
        results = get_exact_phrase_results(search_query)
    elif (query_type == 2):
        results = get_multi_match_results(search_query)
    
    if not results:
        return []

    singers = []
    for i in range(len(results['hits']['hits'])):
        matched = results['hits']['hits'][i]['_source']
        print(matched)
        singer_si = {
            'නම': matched['name_si'],
            'සාරාංශය': matched['summary_si'],
            'පුද්ගලික තොරතුරු': matched['personalInfo_si'],
            'වෘත්තීය තොරතුරු': matched['careerInfo_si'],
            'ගීත': matched['discography_si'],
            'සම්මාන': matched['award_si'],
            'උපන් දිනය': matched['birthDate'],
            'ක්රියාකාරී කාලය': matched['yearsActive_si'],
            'ආරය': matched['genre_si'],
            'link': matched['link']
        }
        singers.append(singer_si)     
    return singers

def find_query_type(query):
    """
    1: exact match search
    2: field specific search
    """

    query_type = 0
    relavant_fields =[]

    if ((query.startswith("'") and query.endswith("'")) or (query.startswith('"') and query.endswith('"'))):
        query_type = 1
        return query_type, relavant_fields, query

    query_terms = clean_query(query).split()
    filtered_query_terms = query_terms.copy()
    for term in query_terms:
        for kw_list in fields:
            keywords = [term]
            keywords.extend(kw_list)
            max_sim = max(check_similarity(keywords))
            if max_sim > 0.8:
                query_type = 2
                relavant_fields.append(kw_list[0])

    if (query_type == 0):
        filtered_query_terms = query_terms

    filtered_query = ' '.join(filtered_query_terms)
    print('query_type:',query_type, 'relavant_fields:', relavant_fields, 'filtered_query:', filtered_query)
    return query_type, relavant_fields, filtered_query

def get_multi_match_results(query):
    results = elasticsearch.search(
        index = Config.index.value, 
        body = {
            "size": 100,
            "query": {
                "multi_match": {
                    "query": query,
                    "type": "best_fields"
            }
        }
    })
    return results

def get_exact_phrase_results(query):
    results = elasticsearch.search(
        index = Config.index.value, 
        body = {
            "size": 100,
            "query": {
                "query_string": {
                    "query": query
            }
        }
    })
    print(results['hits']['hits'])
    return results

def check_similarity(keywords):
    vectorizer = TfidfVectorizer(analyzer="char")
    tfidf_matrix = vectorizer.fit_transform(keywords)
    cs = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
    similarity_results = cs[0][1:]
    return similarity_results


def clean_query(query):
    sw = set(stopwords.words('english'))
    tokens = word_tokenize(query)
    cleaned_query = [x for x in tokens if not x.lower() in sw]

    cleaned_query = [x for x in cleaned_query if not (x == "'s")]
    cleaned_query = ' '.join(cleaned_query).translate(str.maketrans('', '', string.punctuation))
    print('Cleaned query:',cleaned_query)
    return cleaned_query

def translate_to_english(query_si):
    translator = Translator()
    query_en = translator.translate(query_si, dest='si')
    return query_en.text

def translate_to_sinhala(query_en):
    translator = Translator()
    query_si = translator.translate(query_en, dest='en')
    return query_si.text

