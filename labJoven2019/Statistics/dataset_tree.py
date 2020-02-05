import os
import json
from tqdm import tqdm
import pprint


##########
# Este script esta hecho para mis ojos solo... muy feo
##########



# =========
#  SETTINGS
# =========

dataset_path = "/Volumes/NO NAME/Skeens/Datasets/Elisa/"

# =========



# All Categories
# Get names of category folders
folders = []
folder_names = []
for subdirs, dirs, files in os.walk(dataset_path):
	folder_names = dirs
	folders = [dataset_path + d + "/" for d in dirs]
	break



# Messages
# Get names of folders with a messages_1.json file
# and the build the complete paths to be used later
messages_subfolders = ["archived_threads/","inbox/","message_requests/"]
all_message_folders = []
message_users = []
for subfolder in messages_subfolders:
	for subdirs, dirs, files in os.walk(dataset_path+"messages/"+subfolder):
		all_message_folders += [dataset_path+"messages/"+subfolder+user for user in dirs]
		message_users += dirs
		break


# Photos and Videos
albums = []
for subdirs, dirs, files in os.walk(dataset_path+"photos_and_videos/album/"):
	albums = [dataset_path+"photos_and_videos/album/"+f for f in files if not f.startswith(".")]
	break


if "Elisa" in dataset_path:
	master_tag = "elisa_footprint"
else:
	master_tag = "raquel_footprint"
master_json = { master_tag : [] }



idx = 0
for folder in tqdm(folders):

	if ("/messages/" not in folder) and ("/photos_and_videos/" not in folder):
		folder_dict = { folder_names[idx] : [] }
		json_files = []
		for subdirs, dirs, files in os.walk(folder):
			json_files = [folder+f for f in files if (not f.startswith(".")) and (f != "no-data.txt")]
			break
		# Append contents of each file to folder dict
		for f in json_files:
			f = open(f, "r")
			data = json.load(f)
			folder_dict[folder_names[idx]].append(data)
			f.close()
		master_json[master_tag].append(folder_dict)
	else:
		if "/messages/" in folder:
			# Messages
			messages_dict = { "messages" : [] }
			msg_idx = 0
			for message_folder in all_message_folders:
				mf = open(message_folder+"/message_1.json", "r")
				data = json.load(mf)
				user = { message_users[msg_idx] : [] }
				user[message_users[msg_idx]].append(data)
				messages_dict["messages"].append(user)
				msg_idx += 1
				mf.close()
			master_json[master_tag].append(messages_dict)
		else:
			# Photos and Videos
			videos_dict = {"photos_and_videos" : []}
			vf = open(folder+"your_videos.json", "r")
			data = json.load(vf)
			videos_dict["photos_and_videos"].append(data)
			vf.close()

			albums_dict = { "album" : [] }
			v_idx = 0
			for album in albums:	
				vf = open(album, "r")
				data = json.load(vf)
				albums_dict["album"].append(data)
				vf.close()		
			videos_dict["photos_and_videos"].append(albums_dict)
			master_json[master_tag].append(videos_dict)

	idx += 1


f = open("master.json", "w")
pprint.pprint(master_json, f)
f.close()
