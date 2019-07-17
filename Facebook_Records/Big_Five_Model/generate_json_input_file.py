# Libraries
# ---------
import os
import json
import datetime
import subprocess
# Print an error if requests is not installed
try:
	import tqdm
except ImportError:
	print "Error running script: The library tqdm is not installed."
	print "Please follow the instructions on INSTALLATION (first section of the script)."
	exit()



# ====================================
# INSTALLATION
# ====================================
# Run these commands on your terminal.
#  1. Install pip
#		sudo easy-install pip
#	 2. Install requests
#		pip install --user tqdm
# ====================================



# ====================================
#   SETTINGS
# ====================================

dataset_path = '/Volumes/NO NAME/Skeens/Datasets/Elisa/posts/your_posts_1.json'
comments_path = '/Volumes/NO NAME/Skeens/Datasets/Elisa/comments/comments.json'

APIkey = ''

if APIkey == '':
	print "ERROR! No API Key defined. We cannot connect to the IBM server."
	exit()

# ====================================


# ====================================
#   Aux. Functions
# ====================================

# Returns the year in the form of an integer
def get_year(timestamp):
	year = datetime.datetime.fromtimestamp(timestamp).strftime('%Y')
	return int(year)

# Returns the month in the form of an integer
def get_month(timestamp):
	month = datetime.datetime.fromtimestamp(timestamp).strftime('%m')
	return int(month)

# Returns the full date in the form of a string
def get_date(timestamp):
	date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
	return date

# Colors
class colors:
	red = "\033[31m"
	green = "\033[32m"
	blue = "\033[34m"
	light_blue = "\033[94m"
	no_color = "\033[0m"

# ====================================



# ===
# 1.	Load the JSON file with the Facebook data
# ===
f = open(dataset_path, "r")
f_c = open(comments_path, "r")
records = json.load(f)
comment_records = json.load(f_c)
# =======



# ===
# 2.	Create the new JSON structure expected by
#			the IBM server. The structure is as follows:
#			{
#				"contentItems": [
#					{
#						"content": "Ven a vernos a Madrid! Hay pizza...",
#						"created": 123458190834
#					},
#         {
#           "content": "Hoy fui de parranda y perdi el movil...",
#           "created": 123427598555
#         },
#         {
#           "content": "Foto con mi gato <3",
#           "created": 123009999909
#         }
#				]
#			}
#			Each one of these elements correspond to data
#			types in python. For example: ["hi", "there"]
#			is a list, and {"key":"llave", "parrot":"loro"}
#			is a dictionary (or hashtable).	
#
#			Also, we will check the timestamps of each post
#			and when we notice that we reached a post from
#			a new year, we will save the structure into a
#			a new file. This will give us a total of 10
#			files, one for each year.
# ===
# Create the overall holding structure
json_structure = {
	"contentItems": []
}
all_json_structures = []
processed_years = []

total_comments = 0
total_posts = 0

# For each post, extract the content and timestamp
# then add it to the overall structure.
#  *NOTE* Because we may not always have the "post"
#					field, we need to wrap the code around a
#					try/catch block. This makes sure that if
#					the code throws an error because the
#					"post" field is not present, we catch it
#					and ignore it.

comment_records = comment_records["comments"]

idx_com = 0
idx_pos = 0

current_year_com = get_year(int(comment_records[0]["timestamp"]))
current_year_pos = get_year(int(records[0]["timestamp"]))

if (current_year_com > current_year_pos):
	current_year = current_year_com
else:
	current_year = current_year_pos


#for i in range(len(records) + len(comment_records)):
while(idx_com != -1 or idx_pos != -1):

	# Update current year and save structure if necessary
	if (current_year > current_year_pos and current_year > current_year_com):
		all_json_structures.append(json_structure)
		json_structure = {
			"contentItems" : []
		}
		processed_years.append(current_year)
		if (current_year_com > current_year_pos):
			current_year = current_year_com
		else:
			current_year = current_year_pos

	# Check both if there are still comments and posts
	if (idx_com > -1 and idx_pos > -1):
		timestamp_com = int(comment_records[idx_com]["timestamp"])
		timestamp_pos = int(records[idx_pos]["timestamp"])
		if timestamp_com > timestamp_pos:
			# get comment and add comment to structure
			# update idx_com, if no more comments set to -1
			# update current_year_com
			try:
				comment = comment_records[idx_com]["data"][0]["comment"]["comment"]
				item = {
					"content" : "",
					"created" : ""
				}
				item["content"] = comment
				item["created"] = timestamp_com / 1000
				json_structure["contentItems"].append(item)
				#print timestamp_com
				total_comments += 1
			except (KeyError, IndexError) as e:
				pass

			idx_com += 1
			if idx_com >= len(comment_records):
				idx_com = -1
				current_year_com = -1
			else:
				current_year_com = get_year(int(comment_records[idx_com]["timestamp"]))

		else:
			# get post and add it to structure
			# update idx_pos, if no more posts set to -1
			# update current_year_pos
			try:
				post = records[idx_pos]["data"][0]["post"]
				item = {
					"content" : "",
					"created" : ""
				}
				item["content"] = post
				item["created"] = timestamp_pos / 1000
				json_structure["contentItems"].append(item)
				total_posts += 1
			except (KeyError, IndexError) as e:
				pass

			idx_pos += 1
			if idx_pos >= len(records):
				idx_pos = -1
				current_year_pos = -1
			else:
				current_year_pos = get_year(int(records[idx_pos]["timestamp"]))

	elif (idx_com > -1 and idx_pos == -1):
			# get comment and add it
			# update idx_com
			# update current_year_com
			try:
				comment = comment_records[idx_com]["data"][0]["comment"]["comment"]
				timestamp = int(comment_records[idx_com]["timestamp"])
				item = {
					"content": "",
					"created": ""
				}
				item["content"] = comment
				item["created"] = timestamp / 1000
				json_structure["contentItems"].append(item)
				#print timestamp
				total_comments += 1
			except (KeyError, IndexError) as e:
				pass

			idx_com += 1
			if idx_com >= len(comment_records):
				idx_com = -1
				current_year_com = -1
			else:
				current_year_com = get_year(int(comment_records[idx_com]["timestamp"]))

	elif (idx_com == -1 and idx_pos > -1):
			# get post and add it
			# update idx_pos
			# update current_year_pos
			try:
				post = records[idx_pos]["data"][0]["post"]
				timestamp = int(records[idx_pos]["timestamp"])
				item = {
					"content": "",
					"created": ""
				}
				item["content"] = post
				item["created"] = timestamp / 1000
				json_structure["contentItems"].append(item)
				total_posts += 1
			except (KeyError, IndexError) as e:
				pass

			idx_pos += 1
			if idx_pos >= len(records):
				idx_pos = -1
				current_year_pos = -1
			else:
				current_year_pos = get_year(int(records[idx_pos]["timestamp"]))

	else:
			# Done
			break	

# Add the last structure
if current_year_com != -1 or current_year_pos != -1:
	all_json_structures.append(json_structure)
	processed_years.append(current_year)
# =======



# ===
# STATS
# ===
# Compute the total number of posts found
total = 0
for s in all_json_structures:
	total += len(s["contentItems"])
# Print results
print colors.blue
print "Processed a total of " + str(total) + " posts/comments."
print "  Comments: " + str(total_comments) + "."
print "  Posts: " + str(total_posts) + "."
print "Posts/Comments span " + str(len(set(processed_years))) + " years."
print colors.no_color
# ---



# ===
# 3.	Create one file for each year of posts
#			In each JSON file, we will put the structure
#			for its corresponding year.
# ===
# We start by looping x times, where x is the number
# of years we saw on our dataset of posts.
# We use the variable "index" to access the year and
# the JSON structure for that year.
# We then write to the file the structure, and repeat
# this for x iterations.
file_names = []
for index in range(len(processed_years)):
	# Get the year
	year = str(processed_years[index])
	# Create a file name (we use the year as part of the name)
	new_file_name_for_year = "data_" + year + ".json"
	# Add file name to our list
	file_names.append(new_file_name_for_year)
	# Open/Create a file with this name
	f = open(new_file_name_for_year, "w")
	# Write the structure to the file
	json.dump(all_json_structures[index], f)
	# Close the file
	f.close()
# =======



# ===
# 4.	Send posts to IBM's Big Five servers for processing
#
#			In order to send our JSON file to the IBM servers,
#			we will be using the cURL tool. cURL allows us to
#			communicate with the server using a command.
#			We will craft a command for a file, send it, and 
#			save the response from the server to a file. We
#			will repeat this for each year.
#
#			cURL Command based on IBM's servers protocol:
#			curl	-X POST
#						-u "apikey:123abc"
#						--header "Content-Type: application/json"
#						--header "Accept: application/json"
#						--data-binary @posts_2019.json
#						"https://gateway.watsonplatform.net/personality-insights/api/v3/profile?version=2017-10-13&consumption_preferences=true&raw_scores=true"
#
#			Note that the part 123abc of the API key must be
#			replaced by your own API key (obtained on your
#			IBM Big Five model account).
# ===
# Setup the server url and the authentication keys
server_url = "https://gateway.watsonplatform.net/personality-insights/api/v3/profile?version=2017-10-13&consumption_preferences=true&raw_scores=true"
auth = 'apikey:' + APIkey

# Send the request to IBM servers and store results in a file
low_word_count_years = []
insufficient_word_count_years = []
for index in range(len(file_names)):
	# Define the name of the file to store the results in
	filename_big5 = 'big_five_' + str(processed_years[index]) + '.json'
	# Open the file
	f = open(filename_big5, "wb")

	# Construct curl command
	file_name = file_names[index]
	curl_command = [
		"curl", "-X", "POST",
		"-u", auth,
		"--header", "Content-Type: application/json",
		"--header", "Accept: application/json",
		"--data-binary", "@"+file_name,
		server_url
	]
	# Execute curl command
	process = subprocess.call(curl_command, stdout=f)

	# Close the file
	f.close()

	# Keep track of years that had less than 600 words
	# Reopen the file (with reading permision this time)
	f = open(filename_big5, "r")
	# Load the JSON contents
	response = json.load(f)
	try:
		# Get the word count
		word_count = int(response["word_count"])
		#print str(processed_years[index]) + " - " + str(word_count)
		if word_count < 600:
			low_word_count_years.append(processed_years[index])
	except:
		# There was no word count field, so it must have less than the min
		insufficient_word_count_years.append(processed_years[index])

	# Close the file
	f.close()
# =======



# ===
# STATS
# ===
print colors.blue
print "The following years had less than 600 words: "
print low_word_count_years
print "The following years had less than than 100 words, so they have no results:"
print insufficient_word_count_years
print colors.no_color
# =======
