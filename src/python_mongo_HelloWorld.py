##
# Python Sample Application: Connection to Informix using Mongo
##

# Topics
# 1 Inserts
# 1.1 Insert a single document into a collection
# 1.2 Insert multiple documents into a collection
# 2 Queries
# 2.1 Find one document in a collection that matches a query condition  
# 2.2 Find documents in a collection that match a query condition
# 2.3 Find all documents in a collection
# 3 Update documents in a collection
# 4 Delete documents in a collection
# 5 Get a listing of collections
# 6 Drop a collection

from pymongo.mongo_client import MongoClient
import json
import logging
import os
from flask import Flask, render_template

app = Flask(__name__)

# To run locally, set URL and DATABASE information.
# Otherwise, url and database information will be parsed from 
# the Bluemix VCAP_SERVICES.
URL = ""
DATABASE = ""

USE_SSL = False     # Set to True to use SSL url from VCAP_SERVICES
SERVICE_NAME = os.getenv('SERVICE_NAME', 'timeseriesdatabase')
port = int(os.getenv('VCAP_APP_PORT', 8080))

def getDatabaseInfo():
    """
    Get database and url information
    
    :returns: (database, url)
    """
    
    # Use defaults
    if URL and DATABASE:
        return DATABASE, URL
    
    # Parse database info from VCAP_SERVICES
    if (os.getenv('VCAP_SERVICES') is None):
        raise Exception("VCAP_SERVICES not set in the environment")
    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    try:
        tsdb = vcap_services[SERVICE_NAME][0]
        credentials = tsdb['credentials']
        database = credentials['db']
        if USE_SSL:
            url = credentials['mongodb_url_ssl']
        else:
            url = credentials['mongodb_url']
        return database, url
    except KeyError as e:
        logging.error(e)
        raise Exception("Error parsing VCAP_SERVICES. Key " + str(e) + " not found.")

def doEverything():
    # Get database connectivity information
    database, url = getDatabaseInfo()

    # Run test
    try:
        client = MongoClient(url)
        db = client[database]
        
        output = []
        output.append("Starting database test.... ")
        collectionName = "pythonMongo"
        output.append("Creating collection " + collectionName)
        collection = db[collectionName]
        
        #insert 1
        output.append("# 1 Inserts")
        output.append("# 1.1 Insert a single document to a collection")
        collection.insert({"name": "test1", "value": 1})
        output.append("Inserted {\"name\": \"test1\", \"value\": 1}")
        
        #insert many
        output.append("#1.2 Inserting multiple entries into collection")
        multiPost = [{"name": "test1", "value": 1},{"name": "test2", "value": 2}, {"name": "test3", "value": 3}] 
        collection.insert(multiPost)
        output.append("Inserted \n {\"name\": \"test1\", \"value\": 1} \n {\"name\": \"test2\", \"value\": 2} \n {\"name\": \"test3\", \"value\": 3}")
         
        # Find 
        output.append("#2 Queries")
        output.append("#2.1 Find one that matches a query condition")
        output.append(collection.find_one({"name": "test1"}))
         
        # Find all 
        output.append("#2.2 Find all that match a query condition")
        for doc in collection.find({"name": "test1"}):
            output.append(doc)
        
        # Display all documents
        output.append( "#2.3 Find all documents in collection")
        for doc in collection.find():
            output.append(doc)   
        
        # update document
        output.append("#3 Updating Documents")
        collection.update({"name": "test3"}, {"$set": { "value": 4}})
        output.append("Updated test3 with value 4")
         
        # delete document
        output.append("#4 Delete Documents")
        collection.remove({"name": "test2"})  
        output.append("Deleted all with name test2")
        
        # Display all collection names
        output.append("#5 Get a list of all of the collections")
        output.append( db.collection_names())
        
        output.append("#6 Drop a collection")
        db.drop_collection(collectionName)
    
    except Exception as e:
        logging.exception(e) 
        output.append("EXCEPTION (see log for details): " + str(e))
    finally:
        if client is not None:
            client.close()
            output.append("Connection to database has been closed")

    return output

@app.route("/")
def displayPage():
    return render_template('index.html')

@app.route("/databasetest")
def runSample():
    output = []
    try:
        output = doEverything()
    except Exception as e:
        logging.exception(e) 
        output.append("EXCEPTION (see log for details): " + str(e))
    return render_template('tests.html', output=output)

if (__name__ == "__main__"):
    app.run(host='0.0.0.0', port=port)
