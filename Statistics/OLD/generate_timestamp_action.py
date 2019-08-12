import os
import json
import collections
from tqdm import tqdm


# Warning... hay mucho codigo repetido
# y manipulacion del dataset es muy manual.
# No es standard repetir tanto codigo,
# pero esta hecho asi para que sea simple.



# ===============================
#		SETTINGS
# ===============================

dataset_path = "/Volumes/NO NAME/Skeens/Datasets/Elisa/"

results_path = "/Volumes/NO NAME/Skeens/Statistics/Timestamp_Action_Stats/timestamp_action.csv"
results_image_path = "/Volumes/NO NAME/Skeens/Statistics/Timestamp_Action_Stats/timestamp_action_text_image.csv"
stats_path = "/Volumes/NO NAME/Skeens/Statistics/Timestamp_Action_Stats/timestamp_action_stats.csv"

files_to_consider = "ALL"	# could be: "Autoedicion", "Interaccion" or "Facebook_Records"

# ALL
files_to_process = [
	"posts/your_posts_1.json",
	"posts/other_people's_posts_to_your_timeline.json",
	"photos_and_videos/your_videos.json",
	"comments/comments.json",
	"likes_and_reactions/likes_on_external_sites.json",
	"likes_and_reactions/pages.json",
	"likes_and_reactions/posts_and_comments.json",
	"friends/friends.json",
	"friends/rejected_friend_requests.json",
	"friends/removed_friends.json",
	"friends/sent_friend_requests.json",
	"following_and_followers/following.json",
	"following_and_followers/unfollowed_pages.json",
	"messages/archived_threads/",
	"messages/inbox/",
	"messages/message_requests/",
	"groups/your_group_membership_activity.json",
	"events/event_invitations.json",
	"events/your_event_responses.json",
	"events/your_events.json",
	"profile_information/profile_information.json",
	"profile_information/profile_update_history.json",
	"pages/your_pages.json",
	"saved_items_and_collections/saved_items_and_collections.json",
	"your_places/places_you've_created.json",
	"apps_and_websites/apps_and_websites.json",
	"apps_and_websites/posts_from_apps_and_websites.json",
	"other_activity/pokes.json",
	"other_activity/polls_you_voted_on.json",
	"ads/advertisers_you've_interacted_with.json",
	"search_history/your_search_history.json",
	"about_you/your_address_books.json",
	"security_and_login_information/account_activity.json",
	"security_and_login_information/administrative_records.json",
	"security_and_login_information/authorized_logins.json",
	"security_and_login_information/login_protection_data.json",
	"security_and_login_information/logins_and_logouts.json",
	"security_and_login_information/where_you're_logged_in.json"
]

# Autoedicion
autoedicion_files = [
	"posts/your_posts_1.json",
	"photos_and_videos/your_videos.json",
	"likes_and_reactions/likes_on_external_sites.json",
	"likes_and_reactions/pages.json",
	"likes_and_reactions/posts_and_comments.json",
	"following_and_followers/following.json",
	"following_and_followers/unfollowed_pages.json",
	"profile_information/profile_information.json",
	"profile_information/profile_update_history.json",
	"pages/your_pages.json",
	"saved_items_and_collections/saved_items_and_collections.json",
	"your_places/places_you've_created.json",
	"apps_and_websites/apps_and_websites.json",
	"other_activity/pokes.json",
	"other_activity/polls_you_voted_on.json",
	"ads/advertisers_you've_interacted_with.json",
	"search_history/your_search_history.json",
]

# Part of ALL and Autoedicion
albums_path = "photos_and_videos/album/"
last_album_number_elisa = 39
last_album_number_raquel = 15
if "Elisa" in dataset_path:
	last_album_number = last_album_number_elisa
else:
	last_album_number = last_album_number_raquel

# Interaccion
interaccion_files = [
	"posts/other_people's_posts_to_your_timeline.json",
	"comments/comments.json",
	"friends/friends.json",
	"friends/rejected_friend_requests.json",
	"friends/removed_friends.json",
	"friends/sent_friend_requests.json",
	"messages/archived_threads/",
	"messages/inbox/",
	"messages/message_requests/",
	"groups/your_group_membership_activity.json",
	"events/event_invitations.json",
	"events/your_event_responses.json",
	"events/your_events.json",
	"apps_and_websites/posts_from_apps_and_websites.json",
]

# Facebook_Records
facebook_records_files = [
	"about_you/your_address_books.json",
	"security_and_login_information/account_activity.json",
	"security_and_login_information/administrative_records.json",
	"security_and_login_information/authorized_logins.json",
	"security_and_login_information/login_protection_data.json",
	"security_and_login_information/logins_and_logouts.json",
	"security_and_login_information/where_you're_logged_in.json"
]


# ===============================



# ===============================
#		Aux Functions
# ===============================

class colors:
  red = "\033[31m"
  green = "\033[32m"
  blue = "\033[34m"
  light_blue = "\033[94m"
  no_color = "\033[0m"

def write_to_file(file_handler, timestamp, action):
	action = action.encode('ascii', 'ignore')
	file_handler.write(str(timestamp) + ", " + action + "\n")
	
def print_info(filename, action, counter):
	print colors.blue	
	print "Processing file " + filename	
	print "  Action: " + action
	print "  Total actions found: " + str(counter)
	print colors.no_color


def process_file(records, action, rf):
	counter = 0	
	for record in records:
		timestamp = record["timestamp"]
		counter += 1
		write_to_file(rf, timestamp, action)
	return counter


def process_file_other(records, action, rf, timestamp_type):
	counter = 0
	for record in records:
		timestamp = record[timestamp_type]
		counter += 1
		write_to_file(rf, timestamp, action)
	return counter


def process_file_message(records, rf):
	counter = 0
	for record in records:
		timestamp = str(int(record["timestamp_ms"])/1000)
		if "Elisa Cuesta" in record["sender_name"]:
			action = "message_sent"
		else:
			action = "message_received"
		counter += 1
		write_to_file(rf, timestamp, action)
	return counter


def process_file_session(records, action, rf, timestamp_type):
	counter = 0
	for record in records:
		timestamp = record["session"][timestamp_type]
		counter += 1
		write_to_file(rf, timestamp, action)
	return counter


def process_category(records, action, rf, filename):
	counter = process_file(records, action, rf)
	print_info(filename, action, counter)
	return counter


def process_category_other(records, action, rf, filename, mode):
	if mode == "ms":
		counter = process_file_message(records, rf)
	elif mode == "added":
		counter = process_file_other(records, action, rf, "added_timestamp")
	elif mode == "created":
		counter = process_file_other(records, action, rf, "created_timestamp")
	elif mode == "creation":
		counter = process_file_other(records, action, rf, "creation_timestamp")
	elif mode == "start":
		counter = process_file_other(records, action, rf, "start_timestamp")
	elif mode == "session":
		counter = process_file_session(records, action, rf, "created_timestamp")
	else:
		print "ERROR: unknown mode!"
		exit()
	print_info(filename, action, counter)
	return counter


def find_friend_paths(path):
	friends_folder_names = []
	for subdir, dirs, files in os.walk(path):
		friends_folder_names += [path+"/"+f+"/message_1.json" for f in dirs]
		break
	return friends_folder_names

# ===============================



# ===
# Somewhat manually, go through each folder process the data.
# As it's been processed, keep track of how many actions we
# see in total, and add them to the file to avoid memory
# overflows...
# ===

# Determine what files to process
process_albums = False
if files_to_consider == "ALL":
	files = files_to_process
	process_albums = True
elif files_to_consider == "Autoedicion":
	files = autoedicion_files
	process_albums = True
elif files_to_consider == "Interaccion":
	files = interaccion_files
elif files_to_consider == "Facebook_Records":
	files = facebook_records_files
else:
	print colors.red
	print "Error: files_to_consider must have either ALL, Autoedicion, Interaccion, or Facebook_Records"
	print colors.no_color
	exit()

# Open reslts file
rf = open(results_path, "w")

# Process files
total_counter = 0
total_detected_actions = []
for filename in files:

	filename = dataset_path + filename
	if ".json" in filename:
		try:
			f = open(filename, "r")
			records = json.load(f)
		except IOError:
			continue

	# Posts	
	if "/your_posts_1.json" in filename:
		action = "post"
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()

	elif "/other_people's_posts_to_your_timeline.json" in filename:
		action = "wall_post_sent_to_you"
		records = records["wall_posts_sent_to_you"]["activity_log_data"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Photos and Videos
	elif "/your_videos.json" in filename:
		action = "video"
		records = records["videos"]
		total_counter += process_category_other(records, action, rf, filename, "creation")
		total_detected_actions.append(action)

		action = "video_comment"
		for record in records:
			try:
				comments = record["comments"]
				total_counter += process_category(comments, action, rf, filename)
			except KeyError:
				pass
		total_detected_actions.append(action)
		f.close()


	# Comments
	elif "/comments.json" in filename:
		action = "comment"
		records = records["comments"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Likes and Reactions
	elif "/likes_on_external_sites.json" in filename:
		action = "other_like"
		records = records["other_likes"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()

	elif "/pages.json" in filename:
		action = "page_like"
		records = records["page_likes"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()

	elif "/posts_and_comments.json" in filename:
		action = "reaction"
		records = records["reactions"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Friends
	elif "/friends.json" in filename:
		action = "friend"
		records = records["friends"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()

	elif "/rejected_friend_requests.json" in filename:
		action = "rejected_friend_request"
		records = records["rejected_requests"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()

	elif "/removed_friends.json" in filename:
		action = "removed_friend"
		records = records["deleted_friends"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()

	elif "/sent_friend_requests.json" in filename:
		action = "sent_friend_request"
		records = records["sent_requests"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Following and Followers
	elif "/following.json" in filename:
		action = "following"
		records = records["following"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()

	elif "/unfollowed_pages.json" in filename:
		action = "page_unfollowed"
		records = records["pages_unfollowed"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Messages
	elif ("/archived_threads/" in filename) or ("/inbox/" in filename) or ("/message_requests/" in filename):
		action = "message"
		message_file_paths = find_friend_paths(filename)
		for message_file in message_file_paths:
			f = open(message_file, "r")
			records = json.load(f)
			records = records["messages"]
			total_counter += process_category_other(records, action, rf, message_file, "ms")
			f.close()
		action = "message_sent"
		total_detected_actions.append(action)
		action = "message_received"
		total_detected_actions.append(action)


	# Groups
	elif "/your_group_membership_activity.json" in filename:
		action = "group_joined"
		records = records["groups_joined"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Events
	elif "/event_invitations.json" in filename:
		action = "event_invited"
		records = records["events_invited"]
		total_counter += process_category_other(records, action, rf, filename, "start")
		total_detected_actions.append(action)
		f.close()

	elif "/your_event_responses.json" in filename:
		records = records["event_responses"]
		for response_type in records:
			action = response_type.replace(" ", "_")
			total_detected_actions.append(action)
			records_of_type = records[response_type]
			total_counter += process_category_other(records_of_type, action, rf, filename, "start")
		f.close()


	elif "/your_events.json" in filename:
		action = "event_created"
		records = records["your_events"]
		total_counter += process_category_other(records, action, rf, filename, "start")
		total_detected_actions.append(action)
		f.close()


	# Profile Info
	elif "/profile_information.json" in filename:
		action = "profile_registration"
		registration_timestamp = records["profile"]["registration_timestamp"]
		write_to_file(rf, registration_timestamp, action)
		counter = 1
		total_detected_actions.append(action)

		records = records["profile"]["education_experiences"]
		action_start = "started_education_experience"
		action_end = "ended_education_experience"
		total_detected_actions.append(action_start)
		total_detected_actions.append(action_end)
		for record in records:
			try:
				timestamp = record["start_timestamp"]
				write_to_file(rf, timestamp, action_start)
				counter += 1
			except KeyError:
				pass
			try:
				timestamp = record["end_timestamp"]
				write_to_file(rf, timestamp, action_end)
				counter += 1
			except KeyError:
				pass

		total_counter += counter

		print colors.blue
		print "Processing file " + filename
		print "  Actions: " + action + " " + action_start + " " + action_end
		print "  Total actions found: " + str(counter)
		print colors.no_color
		f.close()

	elif "/profile_update_history.json" in filename:
		action = "profile_update"
		records = records["profile_updates"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Pages
	elif "/your_pages.json" in filename:
		action = "page"
		records = records["pages"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Saved Items and Collections
	elif "/saved_items_and_collections.json" in filename:
		action = "save"
		records = records["saves_and_collections"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Your Places
	elif "/places_you've_created.json" in filename:
		action = "created_place"
		records = records["your_places"]
		total_counter += process_category_other(records, action, rf, filename, "creation")
		total_detected_actions.append(action)
		f.close()


	# Apps and Websites
	elif "/apps_and_websites.json" in filename:
		action = "installed_app"
		records = records["installed_apps"]
		total_counter += process_category_other(records, action, rf, filename, "added")
		total_detected_actions.append(action)
		f.close()

	elif "/posts_from_apps_and_websites.json" in filename:
		action = "app_post"
		records = records["app_posts"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Other Activity
	elif "/pokes.json" in filename:
		action = "poke"
		records = records["pokes"]["data"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()

	elif "/polls_you_voted_on.json" in filename:
		action = "poll_vote"
		records = records["poll_votes"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Ads
	elif "/advertisers_you've_interacted_with.json" in filename:
		action = "clicked_on_ad"
		records = records["history"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# Search History
	elif "/your_search_history.json" in filename:
		action = "search"
		records = records["searches"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)
		f.close()


	# About You
	elif "/your_address_books.json" in filename:
		action = "created_contact_on_address_book"
		records = records["address_book"]["address_book"]
		total_counter += process_category_other(records, action, rf, filename, "created")
		total_detected_actions.append(action)
		f.close()


	# Security and Login Info
	elif "/account_activity.json" in filename:
		records = records["account_activity"]
		actions_detected = []
		counter = 0
		for record in records:
			action = record["action"].replace(" ", "_")
			total_detected_actions.append(action)
			actions_detected.append(action)
			timestamp = record["timestamp"]
			counter += 1
			write_to_file(rf, timestamp, action)
		total_counter += counter
		actions_detected = set(actions_detected)
		print colors.blue
		print "Processing file " + filename
		print "  Actions: " + ", ".join(actions_detected)
		print "  Total actions found: " + str(counter)
		print colors.no_color
		f.close()

	elif "/administrative_records.json" in filename:
		records = records["admin_records"]
		actions_detected = []
		counter = 0
		for record in records:
			action = record["event"].replace(" ", "_")
			total_detected_actions.append(action)
			actions_detected.append(action)
			timestamp = record["session"]["created_timestamp"]
			counter += 1
			write_to_file(rf, timestamp, action)
		total_counter += counter
		actions_detected = set(actions_detected)
		print colors.blue
		print "Processing file " + filename
		print "  Actions: " + ", ".join(actions_detected)
		print "  Total actions found: " + str(counter)
		print colors.no_color
		f.close()

	elif "/authorized_logins.json" in filename:
		action = "added_recognized_device"
		records = records["recognized_devices"]
		total_counter += process_category_other(records, action, rf, filename, "created")
		total_detected_actions.append(action)
		f.close()

	elif "/login_protection_data.json" in filename:
		action = "login_protection_data"
		records = records["login_protection_data"]
		total_counter += process_category_other(records, action, rf, filename, "session")
		total_detected_actions.append(action)
		f.close()

	elif "/logins_and_logouts.json" in filename:
 		records = records["account_accesses"]
		actions_detected = []
		counter = 0
		for record in records:
			action = record["action"].replace(" ", "_")
			actions_detected.append(action)
			total_detected_actions.append(action)
			timestamp = record["timestamp"]
			counter += 1
			write_to_file(rf, timestamp, action)
		total_counter += counter
		actions_detected = set(actions_detected)
		print colors.blue
		print "Processing file " + filename
		print "  Actions: " + ", ".join(actions_detected)
		print "  Total actions found: " + str(counter)
		print colors.no_color
		f.close()

	elif "where_you're_logged_in.json" in filename:
		action = "active_session"
		records = records["active_sessions"]
		total_counter += process_category_other(records, action, rf, filename, "created")
		total_detected_actions.append(action)
		f.close()


	# Error
	else:
		print colors.red
		print "Error processing file: " + filename
		print colors.no_color
		exit()


# Process albums (if needed)
if process_albums:

	for idx in range(last_album_number):
		filename = dataset_path + albums_path
		filename = filename + str(idx) + ".json"
		f = open(filename, "r")
		data = json.load(f)

		# Created album timestamp (each file has a last_modified_timestamp) - action: created_album
		#  action: 
		action = "created_album"
		timestamp = data["last_modified_timestamp"]
		write_to_file(rf, timestamp, action)
		total_counter += 1
		total_detected_actions.append(action)

		# In comments:
		#  action: album_comment
		action = "album_comment"
		records = data["comments"]
		total_counter += process_category(records, action, rf, filename)
		total_detected_actions.append(action)

		# In photos:
		#  action: photo_added
		action = "photo_added"
		records = data["photos"]
		total_counter += process_category_other(records, action, rf, filename, "creation")
		total_detected_actions.append(action)

		#	In photos -> comments:
		#		action: photo_comment
		# Process the comments in every photo (if any)
		try:
			action = "photo_comment"
			records = data["photos"]
			for record in records:
				total_counter += process_category(record["comments"], action, rf, filename)	
			
			total_detected_actions.append(action)
			print "photo_comment" in total_detected_actions
		except KeyError:
			pass

		# Skipping because not all have timestamp
		# In cover_photo:
		#	 action: added_album_cover_photo
		#action = "added_album_cover_photo"
		#records = data["cover_photo"]
		#total_counter += process_category_other(records, action, rf, filename, "creation")
		#total_detected_actions.append(action)

		f.close()


# Close file
rf.close()



# ====
# Get stats on new file
# ====
f = open(results_path, "r")
rf = open(stats_path, "w")

action_count = {}
for action in total_detected_actions:
	action_count[action.encode('ascii','ignore')] = 0

action_timestamp = {}
for line in f.readlines():
	cat = line.split()[1]
	action_timestamp[line.split(",")[0]] = cat
	try:
		action_count[cat] += 1
	except KeyError:
		print "Error..."
		print cat
		print line
		#exit()

rf.write("Number of actions: " + str(len(action_count)) + "\n")
rf.write("Total number of timestamps: " + str(total_counter) + "\n")
rf.write("\n")
rf.write("List of action/count:\n")
for action in action_count:
	rf.write(action + ": " + str(action_count[action]) + "\n")



# ====
# STATS
# ====
# remove duplicates
total_detected_actions = set(total_detected_actions)

print colors.blue
print "Total number of unique actions: " + str(len(total_detected_actions))
print "Total number of actions counted: " + str(total_counter)
print
print "List of actions detected:"
print "\n".join(total_detected_actions)
print colors.no_color
# ===


# =======
# Graphic
# =======
dict_file = open("dictionary.csv", "r")
r = open(results_image_path, "w")

dictionary = {}
for line in dict_file.readlines():
	cat = line.split(",")[0]
	char = line.split(",")[1].rstrip()
	dictionary[cat] = char

action_timestamp_sorted = collections.OrderedDict(sorted(action_timestamp.items()))
line_ctr = 0
line_max = 370
lines = 0
for action in action_timestamp.values():
	r.write(dictionary[action])
	line_ctr += 1
	if line_ctr == line_max:
		r.write("\n")
		line_ctr = 0
		lines += 1
	else:
		r.write(" ")

print("Total lines: " + str(lines))

r.close()
dict_file.close()
f.close()
rf.close()


