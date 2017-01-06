import requests
import json
import time
import sys
import os
import datetime
import urllib.request

save_folder = os.getcwd()
vk_chat_const = 2000000000
api = 'https://api.vk.com/method/'
all_photo_messages = []
time_format_string = '%Y.%m.%d %H.%M.%S'

# wrong command format
if (len(sys.argv) < 2):
	print("Usage: 'python [CHAT_ID (find it in chat URL)] [folder where to save (unneccessary, only foldiers without space in name)]'")
	exit(1)

# if directory is specified
elif (len(sys.argv) == 3):
	if (os.path.isdir(sys.argv[2])):
		save_folder = sys.argv[2]
	else:
		exit("This folder doesn't exist and is not creatable")

try:
	chat_id = vk_chat_const + int(sys.argv[1])
except ValueError:
	exit("Chat ID can only be number")

print('Chat ID:',chat_id - vk_chat_const, '\nSave folder:', save_folder)

access_key_url = 'https://oauth.vk.com/authorize'
get_key = requests.get(access_key_url, params = {'client_id': 5804682,
                                                'redirect_uri':'https://oauth.vk.com/blank.html',
                                                'scope':'messages',
                                                'response_type':'token'})
print(get_key.url)


access_token = input("Go to url above, allow to use messages, and copy from URL field \"access_token\"\n");

# finds biggest photo in given dict
def findbiggestsize(photo):
    sizes = ['src_xxxbig', 'src_xxbig', 'src_xbig', 'src_big']
    if sizes[0] in all_photo_sizes:
        return (all_photo_sizes[sizes[0]], all_photo_sizes['created'])

    elif sizes[1] in all_photo_sizes:
        return (all_photo_sizes[sizes[1]], all_photo_sizes['created'])

    elif sizes[2] in all_photo_sizes:
        return (all_photo_sizes[sizes[2]], all_photo_sizes['created'])

    elif sizes[3] in all_photo_sizes:
        return (all_photo_sizes[sizes[3]], all_photo_sizes['created'])


start_from = '0'
count = 0
# exit(1)

while start_from != 'end':
    # getting all attachments
    attachments = requests.get(api + 'messages.getHistoryAttachments', params = {'access_token':access_token,
                                                                            'peer_id':chat_id,
                                                                            'media_type':'photo',
                                                                            'start_from':start_from,
                                                                            'count':200, 
                                                                            'photo_sizes':0})
    # if error - wait some time and continue
    if 'Too many requests per second' in attachments.text:
        print('Too many requests, waiting 4 secs')
        time.sleep(4)
        continue
        
    if attachments.status_code != 200:
    	print("Can't connect to server, check your internet connection. Stopping downloading")
    	break

    # converting to json
    json_attachments = json.loads(attachments.text)['response']
    
    # in order to handle correct number of elements
    if (type(json_attachments) == type({})):
        range_end = len(json_attachments) - 1
    else:
        range_end = len(json_attachments)
    
    # put every image in array
    for i in range(1, range_end):

        if (type(json_attachments) != type([])):
            all_photo_sizes = json_attachments[str(i)]['photo']
        else:
            all_photo_sizes = json_attachments[i]['photo']
            start_from = 'end'

        count += 1
        all_photo_messages.append(findbiggestsize(all_photo_sizes))
    
    if (count%100 == 0):
        print("Working on element", count)
        
    if (start_from == 'end'):
        break
    else:
        start_from = json_attachments['next_from']

print('All photos downloaded. There were total', count)
print('Saving photos')
i = 0
for photo_info in all_photo_messages:
	i += 1
	photo_name = str(i) + '__' + datetime.datetime.fromtimestamp(int(photo_info[1])).strftime(time_format_string) + '.jpg'

	try:
		urllib.request.urlretrieve(all_photo_messages[i][0], save_folder + '\\' + photo_name)
	except:
		time.sleep(7)
	finally:
		urllib.request.urlretrieve(all_photo_messages[i][0], save_folder + '\\' + photo_name)

print('All photos saved to', save_folder)
