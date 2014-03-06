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
from KEEP_FOLLOWING import keep_following
from AUTH_INFO import *


def auto_unfollow(db_file, followed_longer_than=0):
    """ 
       Unfollows users that are not following back and add them to
       the SQLite database.
       Keeps following uses that are in the KEEP_FOLLOWING list.

    Keyword Arguments:
        db_file (str): Path to the .sqlite database file
        older_longer_than (int): unfollows all users that are not following back and were
             followed >= x days ago.

    """
    #connect to sqlite database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    #connect to twitter api
    t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
    
    # get twitter data
    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)['ids'])
    followers = set(t.followers.ids(screen_name=TWITTER_HANDLE)['ids'])
    
    # convert twitter handles into IDs
    users_keep_following = set(t.users.lookup(screen_name=i)[0]['id'] for i in keep_following)
    
    # unfollow users
    not_following_back = following - followers
    cnt = 0
    for user_id in not_following_back:
        try:
            if user_id not in users_keep_following:
                c.execute('INSERT OR IGNORE INTO twitter_db (user_id)' 
                        'VALUES ("{}")'.format(user_id))
                c.execute('SELECT user_id FROM twitter_db WHERE user_id={} '
                          'AND DATE("now") - followed_date >= {}'\
                          .format(user_id, followed_longer_than))
                check = c.fetchone()
                if check:
                    t.friendships.destroy(user_id=user_id)
                    c.execute('UPDATE twitter_db SET unfollowed_date=DATE("now") '
                        'WHERE user_id={}'.format(user_id))
                conn.commit()
                cnt += 1 
                print('unfollowed: {}'.format(t.users.lookup(user_id=user_id)[0]['screen_name']))
                                                                              
        except Exception as e:
            print(e)
            conn.commit()
    
    conn.commit()
    conn.close()
    print('Unfollowed {} users'.format(cnt))  
    return

if __name__ == "__main__":
    
    followed_longer_than = 0
    if len(sys.argv) > 1:
        followed_longer_than = int(sys.argv[1])
                   
    sqlite_file = './follow_db.sqlite'
    auto_unfollow(sqlite_file, followed_longer_than)
