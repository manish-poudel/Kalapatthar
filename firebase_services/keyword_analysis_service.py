from firebase_admin import firestore


class FirebaseKeywordAnalysisService:

    def __init__(self):
        self.firestore_db = firestore.client()

    def getParentDoc(self):
        ref = self.firestore_db.collection(u'share_analysis').document(u'keyword_analysis')
        doc = ref.get()
        return doc

    def updateParentDoc(self, update_data):
        self.firestore_db.collection(u'share_analysis').document(u'keyword_analysis').update(update_data)

    def addAnalysisResult(self, result):
        self.firestore_db.collection(u'share_analysis').document(u'keyword_analysis').collection(
            u'subreddit_analysis').add(result)
