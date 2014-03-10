import subprocess
import time

cnt = 0

while True:
    try:
        subprocess.call('python3 ./auto_follow_back.py', shell=True)
    except:
        print('An Error occurred with: ./auto_follow_back.py')

    print('Sleeping for 16 minutes')
    time.sleep(960) # sleep for 16 minutes


    # follow users only every 3rd iteration of a loop
    if cnt % 3 == 0:
        try:
            subprocess.call('python3 ./auto_follow.py', shell=True)
        except:
            print('An Error occurred with: ./auto_follow.py')

        print('Sleeping for 16 minutes')
        time.sleep(960) # sleep for 16 minutes

    try:
        subprocess.call('python3 ./auto_unfollow.py 1', shell=True)
    except:
        print('An Error occurred with: ./auto_unfollow.py')

    print('Sleeping for 16 minutes')
    time.sleep(960) # sleep for 16 minutes
    
    cnt += 1
    print('This is the {} iteration'.format(cnt))


