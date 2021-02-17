import requests
import csv
from datetime import datetime
import traceback
import time

subreddit = "medicalschool"
url = "https://api.pushshift.io/reddit/{}/search?subreddit={}&limit=1000&sort=desc&before="
start_time = datetime.utcnow()
# start_time = datetime.fromtimestamp(1508889601)
    # Got interrupted, used this to restart where the program halted


def downloadFromUrl(filename, object_type):
    '''
    Should work for pretty much any subreddit
    All that needs to be changed is the subreddit name
    Could use some cleanup, I convert things back and forth
    into strings for probably no reason
    '''
    print(f"Saving {object_type}s to {filename}")
    count = 0
    with open(filename, 'a', newline='') as csvfile:
        previous_epoch = int(start_time.timestamp())
        while True:
            new_url = url.format(object_type, subreddit)+str(previous_epoch)
            while True:
                json = requests.get(new_url, headers={'User-Agent': "FriendlyBot, Ignore"})
                if json.ok:
                    break
            time.sleep(1)
            json_data = json.json()
            if 'data' not in json_data:
                break
            objects = json_data['data']
            if len(objects) == 0:
                break

            for object in objects:
                previous_epoch = object['created_utc'] - 1
                count += 1
                if object_type == 'comment':
                    try:
                        score = (str(object['score']))
                        author = (str(object['author']))
                        # permalink = (str(object['permalink']))
                            # uncomment this if you want. Around 2017, the JSONs appear to
                            # stop using permalink as an object around then and it breaks
                            # this particular script. Almost certainly a way around it
                        date = datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d")
                        btext = object['body']
                        btextASCII = btext.encode(encoding='ascii', errors='ignore').decode()
                        body = (btextASCII)
                        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        spamwriter.writerow([date, author, ' ', score, '"'+body+'"'])
                    except Exception as err:
                        print(f"Couldn't print comment: https://www.reddit.com{object['permalink']}")
                        print(traceback.format_exc())
                elif object_type == 'submission':
                    if object['is_self']:
                        if 'selftext' not in object:
                            continue
                        try:
                            score = (str(object['score']))
                            atext = object['author']
                            atextASCII = atext.encode(encoding='ascii', errors='ignore').decode()
                            author = atextASCII
                            full_link = (str(object['full_link']))
                            date = datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d")
                            stext = object['selftext']
                            stextASCII = stext.encode(encoding='ascii', errors='ignore').decode()
                            selftext = (stextASCII)
                            ttext = object['title']
                            ttextASCII = ttext.encode(encoding='ascii', errors='ignore').decode()
                            title = (ttextASCII)
                            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                            spamwriter.writerow([date, author, full_link, score, '"'+title+'"', '"'+selftext+'"'])
                        except Exception as err:
                            print(f"Couldn't print post: {object['url']}")
                            print(traceback.format_exc())

            print("Saved {} {}s through {}".format(count, object_type, datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d")))

    print(f"Saved {count} {object_type}s")


downloadFromUrl("submissions.csv", "submission")
downloadFromUrl("comments.csv", "comment")
