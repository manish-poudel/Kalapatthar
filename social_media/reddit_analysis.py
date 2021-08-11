from datetime import datetime

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from firebase_admin import firestore
import difflib

from firebase_services.keyword_analysis_service import FirebaseKeywordAnalysisService
from social_media.reddit_data import RedditData


class RedditAnalysis:

    def __init__(self):
        self.firestore_db = firestore.client()
        self.firebase_keyword_analysis_service = FirebaseKeywordAnalysisService()

    def perform_keyword_analysis(self, forum, datatype):
        data = []
        firebase_keyword_analysis_parent_doc = self.firebase_keyword_analysis_service.getParentDoc()
        if firebase_keyword_analysis_parent_doc.exists:

            # Generate token for reddit data request
            reddit_data = RedditData()
            token = reddit_data.get_token()

            # Get keyword data from firestore
            keyword_analysis_parent_data_dict = firebase_keyword_analysis_parent_doc.to_dict()
            keywords_list = keyword_analysis_parent_data_dict['keywords']
            last_post_name = keyword_analysis_parent_data_dict['last_post_name']
            reddit_post_limit = keyword_analysis_parent_data_dict['reddit_post_limit']

            param = {'limit': reddit_post_limit}
            if last_post_name:
                param = {'limit': reddit_post_limit, "before": last_post_name}

            # Get reddit data for the particular forum
            res = reddit_data.get_subreddit(token, forum, datatype, param)

            if res.status_code == 200:
                posts = reddit_data.decode_res(res)
                if posts['data']['children']:
                    for post in posts['data']['children']:
                        text = post['data']['title'] + " " + post['data']['selftext']
                        print("Doing keyword analysis in appended post title and selftext...")
                        keyword_analysis_result = self.keywordCheckInText(text, keywords_list)
                        if keyword_analysis_result:
                            data.append({
                                "title": post['data']['title'],
                                "url": post['data']['url'],
                                "created": datetime.utcfromtimestamp(int(post['data']['created'])).strftime(
                                    '%Y-%m-%d %H:%M:%S'),
                                "name": post['data']['name']
                            })
                    last_post_name = posts['data']['children'][0]['data']['name']

        return {
            "keyword_analysis_data": data,
            "reddit_post_size": len(posts['data']['children']),
            "created_at": datetime.now(),
            "last_post_name": last_post_name
        }

    @staticmethod
    def keywordCheckInText(text, keywords):
        if not text:
            return []
        else:
            print("Tokenizing text...")
            tokenized_words = word_tokenize(text)
            print("Removing stop words...")
            stop_words = set(stopwords.words('english'))
            filtered_words = [word for word in tokenized_words if not word in stop_words]
            print("Stemming words to its root using snow ball stemmer")
            snow_stemmer = SnowballStemmer(language='english')
            stemmed_words = [snow_stemmer.stem(word) for word in filtered_words]

            print("Looping through each words for finding similar words")
            all_similar_words = []
            for word in stemmed_words:
                keyword_similarity = []
                for keyword in keywords:
                    similarity_percentage = difflib.SequenceMatcher(None, word, keyword).ratio() * 100
                    if similarity_percentage >= 90.0:
                        keyword_similarity.append({
                            "keyword": keyword,
                            "similarity_percentage": similarity_percentage
                        })

                if keyword_similarity:
                    all_similar_words.append({
                        "word": word,
                        "word_keyword_similarity": keyword_similarity,
                    })
            return all_similar_words

    def saveDataToFirestore(self, data):
        self.firebase_keyword_analysis_service.addAnalysisResult(data)
        self.firebase_keyword_analysis_service.updateParentDoc({
            "last_post_name": data["last_post_name"]
        })
