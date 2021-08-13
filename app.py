from flask import Flask, request

from social_media.reddit_analysis import RedditAnalysis
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

app = Flask(__name__)
cred = credentials.Certificate("kalapatthar-5643-firebase-adminsdk-b8kkg-8194eb6aeb.json")
firebase_admin.initialize_app(cred)


@app.route('/')
def index():
    return 'share_analysis'


@app.route('/analysis/keyword/subreddit')
def subreddit_analysis():
    load_dotenv()
    api_key = request.args.get('api_key')
    if api_key:
        if api_key != os.environ.get('ANALYSIS_API_KEY'):
            return {"error": "Authentication fail"}
        else:
            reddit_analysis = RedditAnalysis()
            reddit_analysis.perform_keyword_analysis()
            return {"success": "Completed and saved"}
    else:
        return {"error": "Authentication required"}


@app.route('/analysis/subreddit/comment')
def subreddit_comment():
    # Generate token for reddit data request
    # reddit_data = RedditData()
    # token = reddit_data.get_token()
    #
    # # Get reddit comment for the particular post
    # res = reddit_data.get_comment(token)
    # return {
    #     "data": res
    # }

    return "Not implemented"


if __name__ == '__main__':
    app.run(debug=True)
