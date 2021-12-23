import pymongo

client = pymongo.MongoClient('localhost', 27017)
mongodb = client.anonymous_telegram_bot
