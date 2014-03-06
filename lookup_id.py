
from twitter import Twitter, OAuth, TwitterHTTPError
from AUTH_INFO import *

id_set = set(
    ['564185779']
    )

#connect to twitter api
t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))


twitter_names = set(t.users.lookup(screen_name=i)[0]['screen_name'] for i in id_set)
for n in twitter_names:
    print(n)
