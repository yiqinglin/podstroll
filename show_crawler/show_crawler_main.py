from pymongo import MongoClient
import requests
import feedparser
import settings


def main():
    print ('Updating podcast feed url...')
    # self.mongo_uri = settings.MONGO_URI
    # self.mongo_db = settings.MONGO_DATABASE
    # self.mongo_collection = settings.MONGO_COLLECTION

    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DATABASE]
    collection = db[settings.MONGO_COLLECTION]
    podcasts = collection.find({})

    for pod in podcasts:
        podcast_id = pod['podcast_id']
        url = settings.LOOK_UP_BASE + podcast_id
        else:
            try:
                r = requests.get(url)
                data = r.json()
                feed_url = data['results'][0].get('feedUrl', None)
                
                # If podcast has no feedUrl, remove it from the db.
                if not feed_url:
                    print ('removing the podcast as it does not have feed url:', podcast_id)
                    collection.delete_one({'_id': pod['_id']})
                    continue

                # If the feed url returns 404, remove it from the db.
                if requests.get(feed_url).status_code == 404:
                    print ('removing the podcast as it does not have a valid feed url:', podcast_id)
                    collection.delete_one({'_id': pod['_id']})
                    continue

                print ('updating feedUrl to podcast', pod['podcast_id'])
                collection.find_one_and_update({'_id': pod['_id']}, {'$set': {'feed_url': feed_url}})
            except Exception as error:
                print ('Caught this error:', repr(error))

        print ("All done!")


def updatePodcastDetails():
    print ('Updating podcast details using feed url...')

    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DATABASE]
    collection = db[settings.MONGO_COLLECTION]
    podcasts = collection.find({})

    for pod in podcasts:
        feed_url = pod['feed_url']
        print (feed_url)
        d = feedparser.parse(feed_url)
        pod_channel = d['channel']
        

        website_link = pod_channel.get('link', '')
        description = pod_channel.get('description', '')
        summary = pod_channel.get('summary', '')

        pod_img = pod_channel.get('image', None)
        image = pod_img.get('url', '') if pod_img else ''
        pod_type = pod_channel.get('itunes_type', '')
        subtitle = pod_channel.get('subtitle', '')
        itunes_explicit = pod_channel.get('itunes_explicit', '')
        episode_count = len(d.entries)

        print ('Writing into database with detailed information for podcast', pod['podcast_id'])

        collection.find_one_and_update({'_id': pod['_id']}, {'$set': {
            'subtitle': subtitle,
            'website_link': website_link,
            'description': description,
            'summary': summary,
            'pod_type': pod_type,
            'episode_count': episode_count,
            'itunes_explicit': itunes_explicit,
            'image': image
        }})

    print ("All done!")
    

        
        


        



