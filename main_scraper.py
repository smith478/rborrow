import csv
import datetime
import dateutil.parser as parser
import httplib
import nltk
import numpy as np
import os
import os.path
import pandas as pd
import pickle
import praw
import requests
import time
import unicodecsv
import re
import smtplib
import sys
from dateutil import tz
from geopy import geocoders
from subprocess import call

# My libraries
from helpers.custombst import *
from helpers.parsers import *
from helpers.loan_reader import *
from helpers.subs import *
from helpers.user import *


# If true, saves data on newly-encountered loans for modeling later
record_mode = False


# Loads clusters of subreddits
reader = unicodecsv.reader(open("data/srs_tabs.csv", "r"), delimiter="\t")
cluster_dict = {rows[0]:rows[1] for rows in reader}

# Some data on loans
botlist_df = pd.read_csv("data/botlist.csv", sep=";", header=1)

# Data on borrowers and lenders, saved as CustomBSTs
borrower_index = pickle.load(open("rborrow/borrower_index.dat", "r"))
lender_index = pickle.load(open("rborrow/lender_index.dat", "r"))


def email_notification(pdict):
	if pdict["prob"] == -1:
		print("Didn't qualify")
		return

	fromaddr = "gaffney.tj@gmail.com"
	toaddrs  = ["gaffney.tj@gmail.com", "smith478@msu.edu"]
	msg = """New opportunity.
		https://www.reddit.com/r/borrow/comments/{}/ 
		Borrow amount: {} 
		Payback amount: {}
		Loan length: {}
		Probability of payback: {}
		.. """.format(pdict["id"], pdict["borrow"], pdict["payback"], pdict["length"], pdict["prob"])
	username = "gaffney.tj@gmail.com"
	# Replace with password
	password = "****************"
	server = smtplib.SMTP("smtp.gmail.com:587")
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddr, toaddrs, msg)
	server.quit()
	print("EMAIL SENT")


already_done = []
while True:
	# Wait between pings
	time.sleep(2500)

	# Pull last three new posts from r/borrow
	subreddit = praw.Reddit('searchandarchive by ').get_subreddit('borrow')
	for post in subreddit.get_new(limit=3):
		if post.id in already_done:
			continue
		already_done.append(post.id)

		print("---I found a post! It\'s called:{}".format(post))
		url= (post.permalink).replace("?ref=search_posts", "")

		response_json = requests.get(url+".json", headers={"User-Agent": "ClamBot"})
		response = response_json.json()

		# Read the posttype from the parethetical
		is_request = False
		try:
			posttype = response[0][u'data'][u'children'][0][u'data'][u'title'].split("[")[1].split("]")[0].upper()
		except:
			posttype = None
		if posttype == "REQ":
			is_request = True
			this_loan = req_sub(response, url)
			if record_mode:
				write_loan(this_loan)
		elif posttype == "PAID" or posttype == "LATE":
			is_request = False
			if record_mode:
				this_loan = paid_sub(response, url)
				write_loan(this_loan)
		elif posttype == "UNPAID":
			is_request = False
			if record_mode:
				this_loan = paid_sub(response, url)
				this_loan["paid"] = u'N'
				this_loan["deliquent"] = u'Y'
				write_loan(this_loan)

	    if not is_request:
	    	print("Not a request post.")
	    	continue

	    parsed = parse_loan(this_loan, cluster_dict, botlist_df)

		if parsed["borrow"] is not None and (parsed["payback"] is not None or parsed["interest"] is not None):
			# Parsing error
			continue

		# Save to a file
		print(parsed)
		myfile = open("data/Rin/{}.csv".format(parsed["id"]), "wb")
		writer = unicodecsv.writer(myfile)
		#time.sleep(1)
		for key, value in parsed.items():
			writer.writerow([key, value])
		myfile.close()
		
		# Make and run an R file 
		f = open("temp_file", "w")
		f.write("source('modelon.R'); modelon('{}');".format(parsed["id"]))
		f.close()
		call(["r" "temp_file"])

		try:
			g = open("data/Rout/{}".format(parsed["id"]), "r")
			parsed["prob"] = float(g.read())
			g.close()
		except:
			print("R Failure")
			parsed["prob"] = None
			continue
		
		email_notification(parsed)
