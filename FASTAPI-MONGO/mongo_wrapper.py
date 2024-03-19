import pymongo

class MongoWrapper:
    def __init__(self):
        try:

            self.client = pymongo.MongoClient(
                "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000"
            )
            self.client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
            self.db = self.client["PRL_db"]
            self.mail_info = self.db["MailInfo"]
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")