import os
import datetime
import json
import math
from tqdm import tqdm

#####
# Warning!
#  Cada carpeta dentro de "folders" tiene un usuario (friend) unico.
#	 No hay un friend que aparezca en dos folders. Si no fuese el caso,
#  habria de cambiar el script.
#####


# ========================================
#   SETTINGS
# ========================================

interval = 20

dataset_path = '/Volumes/NO NAME/Skeens/Datasets/Elisa/messages'
folders = ["archived_threads", "inbox", "message_requests"]

friends_file_path = '/Volumes/NO NAME/Skeens/Datasets/Elisa/friends/friends.json'

results_settings_path = '/Users/raquelalvarez/Desktop/settings.csv'
results_dataset_path = '/Users/raquelalvarez/Desktop/dataset.csv'

# ========================================



#####
# Debug Message Colors
class colors:
	red = "\033[31m"
	green = "\033[32m"
	blue = "\033[34m"
	light_blue = "\033[94m"
	no_color = "\033[0m"

# Check that the path is valid
if (os.path.exists(dataset_path) is False):
	print colors.red
	print "Error! Path to dataset is invalid. Check the script's Dataset section to fix the path."
	print colors.no_color
	exit()

# Show the user the interval chosen
print colors.green
print "Generating dataset for intervals of " + str(interval) + " minutos."
print colors.no_color
# ---


# Traverse through folders of interest
# to find the path to each friend's message JSON file
# Keep track of 2 lists for reordering later
friends = []
friends_reorder = []
for folder in folders:
	path = dataset_path + "/" + folder
	for subdir, dirs, files in os.walk(path):
		friends = friends + [path+"/"+f+"/message_1.json" for f in dirs]
		friends_reorder = friends_reorder + [path+"/"+f+"/message_1.json" for f in dirs]
		break
# ---



# Gather statistics and reorder friends
# Find the time range
start_timestamp = 1562083908325				# Timestamp later than expected: July 2nd 2019 - 4:12 PM EST
#start_timestamp = 1271611485000			# Start Timestamp for Elisa (caps Raquel's)
end_timestamp = 0

# Load each JSON file and update timestamps accordingly
# For reordering, save a list of the names of friends
friends_names = []
for i in range(len(friends_reorder)):
	with open(friends_reorder[i], "r") as f:
		data = json.load(f)
		# Save the friend name
		friends_names.append(data["participants"][0]["name"])
		# Get timestamp and update bounds accordingly
		for message in data["messages"]:
			message_timestamp = int(message["timestamp_ms"])
			if message_timestamp < start_timestamp:
				start_timestamp = message_timestamp
			if message_timestamp > end_timestamp:
				end_timestamp = message_timestamp

# Rearrange friends
# Now we have:
#		- 2 lists of paths to friends conversations (ordered alphabetically)
#		- 1 list of names of friends (ordered alphabetically)
# To order the friends in the order of acceptance (new to old friends first)
# we need to add the paths one by one to a new list in the order found on
# the friends.json file.
friends_names_sorted = []
with open(friends_file_path, "r") as f:
	data = json.load(f)
	friends_dataset = data["friends"]
	for f in friends_dataset:
		f = f["name"]
		if f in friends_names:
			# For this friend (found in friends.json), find the corresponding index on the paths list
			# then, add the path to the new list of oredered paths
			friends_names_sorted.append(friends_reorder[friends_names.index(f)])
			# Remove the path from the list of paths that we already added (avoid duplicates)
			friends_reorder[friends_names.index(f)] = ""

# In case some conversations were with non-friends, we now
# add the remaining paths to our list (ordered alphabetically)
for f in friends_reorder:
	if f != "":
		friends_names_sorted.append(f)

# Remove any paths that may have been added that
# were not on the original list of paths (such as "")
for new_path in friends_names_sorted:
	if new_path not in friends:
		friends_names_sorted.remove(new_path)

# Set list from old to new friends
friends_names_sorted.reverse()

# Set the list to the new order
friends = friends_names_sorted
# ----



# Print the statistics information for image generation
print colors.light_blue
print "Start Timestamp... " + str(start_timestamp) + " --- " + str(datetime.datetime.fromtimestamp(start_timestamp/1000))
print "End Timestamp... " + str(end_timestamp) + " --- " + str(datetime.datetime.fromtimestamp(end_timestamp/1000))

# Get rid of millisecond precision
start_timestamp /= 1000
end_timestamp /= 1000

# Get rid of seconds precision
start_timestamp /= 60
end_timestamp /= 60

# Max num of pixels needed
pixels = end_timestamp - start_timestamp
#pixels /= 9	# 9 images, 1 per year
print "** Pixels needed to represent in intervals: " + str(pixels)
intervals = [10, 15, 20, 30, 45, 60, 120, 180, 1440]
for i in intervals:
	print "  Intervals of " + str(i) + " min: " + str(pixels/i)
print "The processing script generates an image for each year, roughtly needing the number of pixels / 10."
print colors.no_color
# ---



# Store the length of each conversation
num_of_buckets = (pixels/interval) + 1
max_word_size = 0

# Delete dataset.csv file if already exists
if os.path.isfile(results_dataset_path): 
	os.remove(results_dataset_path)

line = 0
for friend in tqdm(friends):
	# Setup the default values
	word_count_per_bucket = [0 for i in range(num_of_buckets)]
	num_of_messages_per_bucket = [0 for i in range(num_of_buckets)]
	sender_code = [0 for i in range(num_of_buckets)]
	bucket = num_of_buckets - 1
	bucket_threshold = pixels

	# Open the file to start reading messages
	with open(friend, "r") as f:
		data = json.load(f)
		friend_name = data["participants"][0]["name"]

		# Print the lines corresponding to Marcos and Raquel to verify spheres
		#if 'Marcos N' in friend_name:
		if friend_name == "Raquel Alvarez":
			print colors.red
			print line
			print friend_name
			print colors.no_color
		if 'Marcos N' in friend_name:
			print colors.green
			print line
			print friend_name
			print colors.no_color
		line += 1

		# Process each message
		for message in data["messages"]:
			# Get number of words in message
			if 'content' in message:
				message_size = len(message["content"].split())
			else:
				message_size = 0

			# Get timestamp
			message_timestamp = int(message["timestamp_ms"])
			# Reduce the timestamp to minutes
			message_timestamp /= 1000
			message_timestamp /= 60
			# Set timestamp with respect to our timeline
			message_timestamp -= start_timestamp

			# Get bucket if this timestamp is in a past bucket in time
			if (message_timestamp < bucket_threshold) and (message_timestamp < (bucket_threshold - interval)):
				while (message_timestamp < bucket_threshold):
					# Moving to next bucket
					bucket -= 1
					bucket_threshold -= interval
				# Move to the next bucket (while loop leaves bucket off by 1)
				bucket += 1
				bucket_threshold += interval

			# Check for potential overflow (not enough bits to store the total word count)
			if (word_count_per_bucket[bucket] + message_size < word_count_per_bucket[bucket]):
				print colors.red
				print " ERROR ---- OVERFLOW!"
				print colors.no_color
				exit()

			# Add message info
			word_count_per_bucket[bucket] += message_size
			num_of_messages_per_bucket[bucket] += 1

			# Update sender information
			if 'Elisa' in message["sender_name"]:
				# DEBUG
				#if friend_name == "Raquel Alvarez":
				#	print colors.green
				#	print bucket
				#	print colors.no_color
				#	print message
				# -----
				sender_code[bucket] -= 1
			else:
				sender_code[bucket] += 1

		# Close the file
		f.close()

	# Append computed lengths to file and close the file to save memory
	with open(results_dataset_path, "a") as f:
		# DEBUG
		#if (friend_name == "Raquel Alvarez"):
			#f.write("%s\n" % friend_name)
			#buckets_to_test = [174388,145511,128166,128161,128144,94951,79269,77973,71289,71288,71287,68704,35491]
			#for b in buckets_to_test:
				#print colors.green
				#print "Bucket " + str(b) + ": " +  str(word_count_per_bucket[b])
				#print "  Num of messages: " + str(num_of_messages_per_bucket[b])
				#print "  Sender code: " + str(sender_code[b])
				#if (num_of_messages_per_bucket[b] > 0):
				#	total = int(math.ceil(float(word_count_per_bucket[b])/num_of_messages_per_bucket[b]))
				#	total = total * (abs(sender_code[b])/sender_code[b])
				#else:
				#	total = 0
				#print "  Stored: " + str(total)
				#print colors.no_color
		# -----

		# Write values comma separated
		for b in range(len(word_count_per_bucket)):
			# Compute avg message size for the bucket and set the code (Elisa/Other)
			if (num_of_messages_per_bucket[b] > 0):
				total = int(math.ceil(float(word_count_per_bucket[b])/num_of_messages_per_bucket[b]))
				# Update longest word count before setting the sign
				if total > max_word_size:
					max_word_size = total
				# Set the sign (negative = Elisa, positive = Other) to encode who spoke the most
				if (sender_code[b] != 0):
					total = total * (abs(sender_code[b])/sender_code[b])	# negative values correspond to Elisa
			else:
				total = 0
			# Write the value to the file
			f.write("%d," % total)
		
		# Move cursor to a new line
		f.write("\n")

		# Close the file
		f.close()

print "Length of the longest message: " + str(int(max_word_size))
# ---


# Write the dataset settings to the file
with open(results_settings_path, "w") as f:
	f.write("%d\n" % interval)
	f.write("%d\n" % len(friends))
	f.write("%d\n" % num_of_buckets)
	f.write("%d\n" % max_word_size)
	f.close()
# ---
