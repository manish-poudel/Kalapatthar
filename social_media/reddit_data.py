import requests
import os
from dotenv import load_dotenv
from datetime import datetime


class RedditData:

    def __init__(self):
        load_dotenv()

    @staticmethod
    def get_token():
        auth = requests.auth.HTTPBasicAuth(os.environ.get('REDDIT_CLIENT_ID'), os.environ.get('REDDIT_SECRET_TOKEN'))
        data = {'grant_type': 'password',
                'username': os.environ.get('REDDIT_USERNAME'),
                'password': os.environ.get('REDDIT_PASSWORD')}
        headers = {'User-Agent': 'KalaPatthar/1.0.0'}

        res = requests.post('https://www.reddit.com/api/v1/access_token',
                            auth=auth, data=data, headers=headers)

        token = res.json()['access_token']
        return token

    @staticmethod
    def get_subreddit(token, subreddit, data_type, params):
        headers = {**{'User-Agent': 'KalaPatthar/1.0.0'}, **{'Authorization': f"bearer {token}"}}
        res = requests.get("https://oauth.reddit.com/r/" + subreddit + "/" + data_type,

                           headers=headers, params=params)
        return res

    @staticmethod
    def decode_res(res):
        decode_response = None
        try:
            decode_response = res.json()
        except ValueError:
            return decode_response
        finally:
            return decode_response

    @staticmethod
    def get_comment(token):
        headers = {**{'User-Agent': 'KalaPatthar/1.0.0'}, **{'Authorization': f"bearer {token}"}}
        res = requests.get("https://oauth.reddit.com/r/ausstocks/comments/oygnc0/invex_therapeutics_due_diligence/",
                           headers=headers, params={'limit': 2})
        return res.json()

    @staticmethod
    def get_filtered_subreddit(posts):
        filtered_posts = []
        for post in posts['data']['children']:
            filtered_post = {
                "title": post['data']['title'],
                "selftext": post['data']['selftext'],
                "created": datetime.utcfromtimestamp(int(post['data']['created'])).strftime('%Y-%m-%d %H:%M:%S'),
                "name": post['data']['name'],
                "score": post['data']['score'],
                "ups": post['data']['ups'],
                "downs": post['data']['downs'],
                "url": post['data']['url'],
                "subreddit_subscribers": post['data']['subreddit_subscribers'],
                "upvote_ratio": post['data']['upvote_ratio']
            }
            filtered_posts.append(filtered_post)
        return filtered_posts
