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
from twitter import Twitter, OAuth, TwitterHTTPError
from DONT_FOLLOW import dont_follow
from AUTH_INFO import *


def auto_follow_followers(db_file):
    """ Follows everyone back who has followed you."""
    
    #connect to sqlite database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    #connect to twitter api
    t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
    
    # get twitter data    
    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    followers = set(t.followers.ids(screen_name=TWITTER_HANDLE)["ids"])

    not_following_back = followers - following
    users_dont_follow = set(t.users.lookup(screen_name=i)[0]['id'] for i in dont_follow)

    cnt = 0
    for user_id in not_following_back:
        if user_id not in users_dont_follow:
            try:
                t.friendships.create(user_id=user_id)
                cnt += 1                
                c.execute('INSERT OR IGNORE INTO twitter_db (user_id, followed_date) ' 
                    'VALUES ("{}", DATE("now"))'.format(user_id))
                c.execute('UPDATE twitter_db SET followed_date=DATE("now") '
                        'WHERE user_id={}'.format(user_id))
                conn.commit()
                print("followed: {}".format(t.users.lookup(user_id=user_id)[0]['screen_name']))

            except Exception as e:
                print(e)
    print('Followed back %s users' %cnt)
    return



if __name__ == '__main__':
    sqlite_file = './follow_db.sqlite'
    auto_follow_followers(sqlite_file)

