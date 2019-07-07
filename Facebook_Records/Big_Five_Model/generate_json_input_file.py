# Libraries
# ---------
import os
import json
import datetime
import subprocess
# Print an error if requests is not installed
try:
	import requests
except ImportError:
	print "Error running script: The library requests is not installed."
	print "Please follow the instructions on INSTALLATION (first section of the script)."
	exit()



# ====================================
# INSTALLATION
# ====================================
# Run these commands on your terminal.
#  1. Install pip
#		sudo easy-install pip
#	 2. Install requests
#		pip install --user requests
# ====================================



# ====================================
#   SETTINGS
# ====================================

dataset_path = '/Volumes/NO NAME/Skeens/Datasets/Elisa/posts/your_posts_1.json'

APIkey = ''

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
records = json.load(f)
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

# For each post, extract the content and timestamp
# then add it to the overall structure.
#  *NOTE* Because we may not always have the "post"
#					field, we need to wrap the code around a
#					try/catch block. This makes sure that if
#					the code throws an error because the
#					"post" field is not present, we catch it
#					and ignore it.
current_year = get_year(int(records[0]["timestamp"]))   # extract the year from this timestamp
#print "Starting with... " + str(current_year)
for record in records:
	if True:
		# Get the timestamp
		timestamp = int(record["timestamp"])		# convert to UNIX before passing to JSON file
		year = get_year(timestamp)

		# Get post content
		try:
			# If there is a post tag, get the post
			data_field = record["data"][0]
			post_content = data_field["post"]
		except:
			# If there is no post tag, set the variable to ""
			# print "No post content"
			continue

		# Check to make sure that this post is still
		# within the current year, otherwise save the
		# posts already stored and move on to the next
		# year
		if year < current_year:
			# Add this year's structure to our list
			all_json_structures.append(json_structure)
			# Remove the posts since we are using this for a new year
			json_structure = {
				"contentItems": []
			}
			# Add processed year to our list
			processed_years.append(current_year)
			# Set the year to the new one
			current_year = year

		# Build the new record
		item = {
			"content": "",
			"created": ""
		}
		item["content"] = post_content
		item["created"] = timestamp / 1000		# UNIX Timestamp is seconds only

		# Store the post on our structure
		json_structure["contentItems"].append(item)

#	except:
		# No "post" tag on JSON field, so we keep going
#		continue
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
print "Processed a total of " + str(total) + " posts."
print "Posts span " + str(len(processed_years)) + " years."
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
	new_file_name_for_year = "posts_" + year + ".json"
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
