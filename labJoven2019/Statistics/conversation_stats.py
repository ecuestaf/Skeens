import os
import json
from tqdm import tqdm


# ! PLEASE CREATE A FOLDER NAMED conversation_results
# ! TO AVOID ERRORS...

# ======================================
#		SETTINGS
# ======================================

dataset_path = '/Volumes/NO NAME/Skeens/Datasets/Elisa/messages'
folders = ["archived_threads", "inbox", "message_requests"]

results_path = '/Volumes/NO NAME/Skeens/Statistics/conversation_stats.csv'

# ======================================



# ======================================
#		Aux. Functions/Classes
# ======================================

# Terminal Output Colors
class colors:
  red = "\033[31m"
  green = "\033[32m"
  blue = "\033[34m"
  light_blue = "\033[94m"
  no_color = "\033[0m"

# ======================================



# Find the path to each friend's message JSON file
friends = []
friend_folder_names = []
for folder in folders:
	path = dataset_path + "/" + folder
	for subdir, dirs, files in os.walk(path):
		friends = friends + [path + "/" + f + "/message_1.json" for f in dirs]
		friend_folder_names = friend_folder_names + [f for f in dirs]
		break
# ---



# Store the stats of each conversation on a list
#		Stats: timestamp, sent(1)/received(0), size(num of words)
for index in tqdm(range(len(friends))):
	# Open the Facebook conversation JSON file
	conv_file = open(friends[index], "r")
	# Open a new file to save this conversation stats
	results_file= open("conversation_results/" + friend_folder_names[index] + ".csv", "w")
	
	# Get the JSON data
	data = json.load(conv_file)

	# Flag to get sender's name
	first_message = True

	# Process all messages
	for m in data["messages"]:
		# Add name to the file
		if first_message:
			try:
				results_file.write(str(m["sender_name"]) + "\n")
			except UnicodeEncodeError:
				results_file.write(friend_folder_names[index] + "\n")
			first_message = False
		# Store the timestamp
		timestamp = m["timestamp_ms"]
		# Store the sender
		sender = m["sender_name"]
		if sender == "Elisa Cuesta Fernandez":
			sent = 1
		else:
			sent = 0
		# Store the size
		try:
			size = len(m["content"].split())
		except:
			# If no post, skip this message
			continue
		# Save the message
		results_file.write(str(timestamp) + ", " + str(sent) + ", " + str(size) + "\n")

	# Close files
	conv_file.close()
	results_file.close()
