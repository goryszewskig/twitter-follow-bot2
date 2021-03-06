"""
Copyright 2014 Sebastian Raschka and Randal S. Olson
Original project: https://github.com/rhiever/twitter-follow-bot


This file is part of the Twitter Follow Bot2 library.

The Twitter Follow Bot2 library is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option) any
later version.

The Twitter Follow Bot library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with the Twitter
Follow Bot library. If not, see http://www.gnu.org/licenses/.

"""

import sqlite3
import sys
from twitter import Twitter, OAuth, TwitterHTTPError
import QUERIES
from AUTH_INFO import *
from DONT_FOLLOW import dont_follow


def print_results(stats_dict):
    """
    Prints stats of how many people were followed.

    """
    print('\nQuery,already_friends,already_in_db,new_followers,total_tweets_queried')
    totals = [0,0,0,0]
    for q in stats_dict.keys():
        print('%s,%s,%s,%s,%s' %(q, stats_dict[q][0], stats_dict[q][2],
                 stats_dict[q][1], stats_dict[q][3])
             )
        totals[0] += stats_dict[q][0]
        totals[2] += stats_dict[q][2]
        totals[1] += stats_dict[q][1]
        totals[3] += stats_dict[q][3]
    print(30 * '-')
    print('already friends: %s\nalready in db: %s\n'\
          'new users following: %s\ntotal tweets queried: %s'\
            %(totals[0], totals[2], totals[1], totals[3]))
    print(30 * '-')

    return


def auto_follow_loop(queries, db_file, count=10, result_type="recent"):
    """
    Auto-follows people that have not been followed before and match words
    in the QUERIES list.
    Adds new followers to SQLite database.    

    """
    
    #connect to twitter api
    t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

    #connect to sqlite database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    stats = dict()
    # search for query term, follow matched users and append user id to sqlite db 

    cnt = 0     
    for q in queries:
        result = t.search.tweets(q=q, result_type=result_type, count=count)
        following = set(t.friends.ids(screen_name=TWITTER_HANDLE)['ids'])
        stats[q] = [0,0,0, len(following)] 

        # also don't follow users that are in DONT_FOLLOW.py
        users_dont_follow = set(t.users.lookup(screen_name=i)[0]['id'] for i in dont_follow)
        following.union(users_dont_follow)   
         
        # stats for found_friends, new_followers, followers_in_db, search_results
        for tweet in result['statuses']:
            try:
                if tweet['user']['screen_name'] != TWITTER_HANDLE and tweet['user']['id'] not in following:
                    
                    # check if user ID is already in sqlite database
                    c.execute('SELECT user_id FROM twitter_db WHERE user_id={}'.format(tweet['user']['id']))
                    check=c.fetchone()
                    if not check:
                        t.friendships.create(user_id=tweet['user']['id'])
                        following.update(set([tweet['user']['id']]))
                        print('following {}'.format(tweet['user']['screen_name']))
                        # add new ID to sqlite database
                        c.execute('INSERT INTO twitter_db (user_id, followed_date) ' 
                        'VALUES ("{}", DATE("now"))'.format(tweet['user']['id']))
                        conn.commit()
                        stats[q][1] += 1
                    else:
                        stats[q][2] += 1
                else:
                    stats[q][0] += 1
                 
            except TwitterHTTPError as err:
                c.execute('SELECT user_id FROM twitter_db WHERE user_id={}'.format(tweet['user']['id']))
                check=c.fetchone()
                if not check:
                    c.execute('INSERT INTO twitter_db (user_id, followed_date) VALUES ("%s", DATE("now"))' %tweet['user']['id'])
                    conn.commit()
                print("error: ", err)
                sys.exit()
    
                # quit on error unless it's because someone blocked me
                if "blocked" not in str(err).lower():
                    conn.commit()
                    conn.close()
                    print(print_results(stats))
                    quit()
            finally:
                # always update database to accommodate for unexpected crashes
                conn.commit()

    conn.close()
    print(print_results(stats))
    return


if __name__ == "__main__":
                       
    sqlite_file = './follow_db.sqlite'
    auto_follow_loop(QUERIES.queries, sqlite_file, count=100, result_type="recent")
