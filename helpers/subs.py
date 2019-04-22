# -*- coding: utf-8 -*-

def req_sub(p_response, p_url):
	thisloan=dict()					
	thisloan["source_control"]=88888
	thisloan["request_filled_fromflair"]="N"
	if p_response[0][u'data'][u'children'][0][u'data'][u'link_flair_text']==u'Completed':
		thisloan["request_filled_fromflair"]="Y"
	thisloan["id"]=p_response[0][u'data'][u'children'][0][u'data'][u'id']
	thisloan["error"]=0
	thisloan["borrower"]=p_response[0][u'data'][u'children'][0][u'data'][u'author'].lower()
	thisloan["request_title"]=p_response[0][u'data'][u'children'][0][u'data'][u'title']
	thisloan["request_header"]=p_response[0][u'data'][u'children'][0][u'data'][u'selftext']
	thisloan["request_comments"]=list()
	for i in range(len(p_response[0][u'data'][u'children'])):
		if p_response[0][u'data'][u'children'][i][u'data'][u'author'] not in [u'LoansBot',u'AutoModerator']:
			thisloan["request_comments"].append(p_response[0][u'data'][u'children'][i][u'data'][u'selftext'])
	thisloan["request_date"]=datetime.datetime.utcfromtimestamp(p_response[0][u'data'][u'children'][0][u'data'][u'created'])
	thisloan["target_date"]=u'NULL'
	thisloan["amount"]=u'NULL'
	thisloan["currency"]=u'NULL'
	thisloan["payback_amount"]=u'NULL'
	for par in p_response[0][u'data'][u'children'][0][u'data'][u'title'].split("("):
		#First look inside a parenthetical.  For newer posts
		if thisloan["target_date"]==u'NULL':
			thisloan["target_date"]=parse_date(par.split(")")[0],borrow_date=thisloan["request_date"])
		if thisloan["amount"]==u'NULL':
			thisloan["amount"]=parse_currency(par.split(")")[0])["amount"]
			thisloan["currency"]=parse_currency(par.split(")")[0])["currency"]
	#Then look in the title generally
	if thisloan["target_date"]==u'NULL':
		#Exception handle, since very special cases can break it.
		try:
			thisloan["target_date"]=parse_date(thisloan["request_title"],borrow_date=thisloan["request_date"])
		except:
			assert(True)
	#Then look in the body of the post.  Currently this does nothing.
	if thisloan["target_date"]==u'NULL':
		try:
			thisloan["target_date"]=parse_date(thisloan["request_header"],borrow_date=thisloan["request_date"],inbody=1)
		except:
			assert(True)
	#Critical Errors
	if thisloan["target_date"]==u'NULL':
		thisloan["error"]+=1
		#broken_urls.append(p_url)
		#print "Can't figure out target date"
		thisloan["due"]="Unknown"
	else:
		if datetime.date.today()>thisloan["target_date"].date():
			thisloan["due"]="Y"
		else:
			thisloan["due"]="N"
	if thisloan["amount"]==u'NULL':
		thisloan["error"]+=2
		#broken_urls.append(p_url)
		#print "Can't figure out amount"
	else:
		locarr=re.split("[$£€]",thisloan["request_title"].replace("$"+str(thisloan["amount"]),"").replace(str(thisloan["amount"])+"$",""))
		num_dollarsigns=len(locarr)-1
		if num_dollarsigns==1:
			thisloan["payback_structure"]=u'Simple'
			if locarr[1].lstrip(" ")[:1]>="0" and locarr[1].lstrip(" ")[:1]<="9":
				l=0
				while locarr[1].lstrip(" ")[l]>="0" and locarr[1].lstrip(" ")[l]<="9":
					l+=1
				thisloan["payback_amount"]=int(locarr[1].lstrip(" ")[:l])
			elif locarr[0].rstrip(" ")[-1:]>="0" and locarr[0].rstrip(" ")[-1:]<="9":
				l=-1
				while (locarr[0].rstrip(" ")[1]>="0" and locarr[0].rstrip(" ")[1]<="9") or locarr[0].rstrip(" ")[1]==".":
					l-=1
				thisloan["payback_amount"]=int(float(locarr[0].rstrip(" ")[l:]))
			else:
				thisloan["payback_structure"]=u'Unknown'
				thisloan["payback_amount"]=u'Unknown'
		elif num_dollarsigns>1:
			thisloan["payback_structure"]=u'Complex'
			thisloan["payback_amount"]=u'Unknown'
		else:
			thisloan["payback_structure"]=u'Unknown'
			thisloan["payback_amount"]=u'Unknown'
			for sentence in thisloan["request_header"].split("."):
				if sentence.find("interest")!=-1 and sentence.find("repa")!=-1:
					locarr=re.split("[$£€]",sentence.replace("$"+str(thisloan["amount"]),"").replace(str(thisloan["amount"])+"$",""))
					num_dollarsigns=len(locarr)-1
					if num_dollarsigns==1:
						thisloan["payback_structure"]=u'Simple'
						if locarr[1].lstrip(" ")[:1]>="0" and locarr[1].lstrip(" ")[:1]<="9":
							l=0
							while locarr[1].lstrip(" ")[l]>="0" and locarr[1].lstrip(" ")[l]<="9":
								l+=1
							thisloan["payback_amount"]=int(locarr[1].lstrip(" ")[:l])
						elif locarr[0].rstrip(" ")[-1:]>="0" and locarr[0].rstrip(" ")[-1:]<="9":
							l=-1
							while (locarr[0].rstrip(" ")[1]>="0" and locarr[0].rstrip(" ")[1]<="9") or locarr[0].rstrip(" ")[1]==".":
								l-=1
							thisloan["payback_amount"]=int(float(locarr[0].rstrip(" ")[-l:]))
						else:
							thisloan["payback_structure"]=u'Unknown'
							thisloan["payback_amount"]=u'Unknown'
					elif num_dollarsigns>1:
						thisloan["payback_structure"]=u'Complex'
						thisloan["payback_amount"]=u'Unknown'
	if thisloan["payback_amount"]!=u'Unknown' and thisloan["payback_amount"]<thisloan["amount"]:
		thisloan["payback_amount"]+=thisloan["amount"]
	#Moved down here to give payback_amount an organic shot.
	#Then look in the title generally
	if thisloan["amount"]==u'NULL':
		try:
			grabbinmydict=parse_currency_string(thisloan["request_title"])
			thisloan["amount"]=grabbinmydict["borrow"]
			thisloan["currency"]=grabbinmydict["currency"]
			thisloan["payback_amount"]=grabbinmydict["payback"]
			thisloan["source_control"]=grabbinmydict["source_control"]
		except:
			assert(True)
	#Then look in the body of the post.  Currently this does nothing.
	if thisloan["amount"]==u'NULL':
		try:
			grabbinmydict=parse_currency_string(thisloan["request_header"],inbody=1)
			thisloan["amount"]=grabbinmydict["borrow"]
			thisloan["currency"]=grabbinmydict["currency"]
			thisloan["payback_amount"]=grabbinmydict["payback"]
			thisloan["source_control"]=grabbinmydict["source_control"]
		except:
			assert(True)
	thisloan["actual_date"]=u'NULL'
	thisloan["paid_header"]=u'NULL'
	thisloan["paid_comments"]=list()
	if p_response[0][u'data'][u'children'][0][u'data'][u'link_flair_text']==u'Completed':
		thisloan["written"]=u'Y'
		thisloan["lender"]=u'NULL'
		for i in range(len(p_response[1][u'data'][u'children'])):
			if p_response[1][u'data'][u'children'][i][u'data'][u'body'].find("$loan")!=-1:
				thisloan["lender"]=p_response[1][u'data'][u'children'][i][u'data'][u'author'].lower()
		#Critical error
		if thisloan["lender"]==u'NULL':
			thisloan["error"]+=4
			#broken_urls.append(p_url)
			#print "Completed without lender error"
	else:
		thisloan["written"]=u'N'
		thisloan["lender"]=u'NULL'
	thisloan["paid"]=u'N'
	thisloan["schedule"]=u'NULL'
	thisloan["deliquent"]=u'Unknown'
	thisloan["deliquent_header"]=u'NULL'
	thisloan["deliquent_comments"]=list()
	thisloan["medium"]=list()
	for s in media:
		#Replace piece is for e-transfer
		if p_response[0][u'data'][u'children'][0][u'data'][u'title'].lower().replace("-","").find(s)!=-1:
			thisloan["medium"].append(s)
	thisloan["url_req"]=p_response[0][u'data'][u'children'][0][u'data'][u'url']
	thisloan["url_paid"]=u'NULL'
	thisloan["url_unpaid"]=u'NULL'
	locget=p_response[0][u'data'][u'children'][0][u'data'][u'title'].split("(#")
	if len(locget)>1:
		thisloan["location_raw"]=locget[1].split(")")[0]
		try:
			place,[lat,lon]=geocoders.GoogleV3().geocode(thisloan["location_raw"])
			thisloan["location_Google"]=place
			thisloan["location_timezone"]=geocoders.GoogleV3().timezone((lat,lon))
		except:
			thisloan["location_Google"]=u'NULL'
			thisloan["location_timezone"]=u'NULL'
		locpartsget=thisloan["location_raw"].split(",")
		if len(locpartsget)==3:
			thisloan["location_city"]=locpartsget[0].lstrip(" ").rstrip(" ").lower()
			thisloan["location_state"]=locpartsget[1].lstrip(" ").rstrip(" ").lower()
			thisloan["location_country"]=locpartsget[2].lstrip(" ").rstrip(" ").lower()
		else:
			thisloan["location_city"]=u'Unknown'
			thisloan["location_state"]=u'Unknown'
			thisloan["location_country"]=u'Unknown'
	else:
		thisloan["location_raw"]=u'NULL'
		thisloan["location_Google"]=u'NULL'
		thisloan["location_timezone"]=u'NULL'
		thisloan["location_city"]=u'NULL'
		thisloan["location_state"]=u'NULL'
		thisloan["location_country"]=u'NULL'
	thisloan["timestamp"]=p_response[0][u'data'][u'children'][0][u'data'][u'created']
	thisloan["score"]=p_response[0][u'data'][u'children'][0][u'data'][u'score']
	thisloan["ups"]=p_response[0][u'data'][u'children'][0][u'data'][u'ups']
	thisloan["upvote_ratio"]=p_response[0][u'data'][u'children'][0][u'data'][u'upvote_ratio']
	if thisloan["location_timezone"]==u'NULL':
		thisloan["hour"]=u'NULL'
		thisloan["weekday"]=datetime.datetime.utcfromtimestamp(thisloan["timestamp"]).weekday()
	else:
		holdtime=datetime.datetime.utcfromtimestamp(thisloan["timestamp"]).replace(tzinfo=tz.tzutc()).astimezone(thisloan["location_timezone"])
		thisloan["hour"]=holdtime.hour
		thisloan["weekday"]=holdtime.weekday()
	thisloan["match_execption"]=0
	thisloan["late"]=u'N'
	return thisloan

def paid_sub(p_response,p_url):
	thisloan=dict()	
	#print(p_url)
	#As a first-step look for this bot in newer posts
	found=False
	for i in range(len(p_response[1][u'data'][u'children'])):
		if p_response[1][u'data'][u'children'][i][u'data'][u'body'].find("$paid")!=-1 and p_response[1][u'data'][u'children'][i][u'data'][u'replies']<>u'':
			for j in range(len(p_response[1][u'data'][u'children'][i][u'data'][u'replies'][u'data'][u'children'])):
				if p_response[1][u'data'][u'children'][i][u'data'][u'replies'][u'data'][u'children'][j][u'data'][u'body'].find("Original Thread")!=-1 and not found:
					orig_id=p_response[1][u'data'][u'children'][i][u'data'][u'replies'][u'data'][u'children'][j][u'data'][u'body'].split("/comments/")[1].split("/")[0]
					found=True
	#print(found)
	if found:
		#print("First found")
		thisloan=readLoan(orig_id)
		thisloan["match_exception"]=0
	#print(found)
	if not found:
		#print("Not found")
		#When we can't find the original, then we look up by lender
		#This is impercise, so we flag match_exception
		lender=p_response[0][u'data'][u'children'][0][u'data'][u'author']
		lendee=""
		#print(lender)
		#First see if there is a "u/" in there
		if not found and p_response[0][u'data'][u'children'][0][u'data'][u'title'].find("u/")!=-1:
			for u in p_response[0][u'data'][u'children'][0][u'data'][u'title'].lower().split():
				if u.find("u/")!=-1:
					lendee=u.replace("u/","").replace("/","").replace("[","").replace("]","")
		if not found and lendee!="":
			holdloan=findLoan(lender_index,borrower_index,p_lender=lender,p_borrower=lendee)
			if holdloan["candidates"]>0:
				found2at=holdloan["filename"]
				found=True
				if holdloan["candidates"]==1:
					mymatch=1
				else:
					mymatch=2
			if not found:
				holdloan=findLoan(lender_index,borrower_index,p_borrower=lendee)
				if holdloan["candidates"]>0:
					found2at=holdloan["filename"]
					found=True
					if holdloan["candidates"]==1:
						mymatch=3
					else:
						mymatch=4
		if not found:
			lendee=p_response[0][u'data'][u'children'][0][u'data'][u'title'].replace("[PAID]","").replace("[LATE]","").lower().split()[0]
		if not found and lendee!="":
			holdloan=findLoan(lender_index,borrower_index,p_lender=lender,p_borrower=lendee)
			if holdloan["candidates"]>0:
				found2at=holdloan["filename"]
				found=True
				if holdloan["candidates"]==1:
					mymatch=1
				else:
					mymatch=2
			if not found:
				holdloan=findLoan(lender_index,borrower_index,p_borrower=lendee)
				if holdloan["candidates"]>0:
					found2at=holdloan["filename"]
					found=True
					if holdloan["candidates"]==1:
						mymatch=3
					else:
						mymatch=4
		if not found:
			holdloan=findLoan(lender_index,borrower_index,p_lender=lender)
			if holdloan["candidates"]>0:
				found2at=holdloan["filename"]
				found=True
				if holdloan["candidates"]==1:
					mymatch=5
				else:
					mymatch=6
		if found:
			thisloan=readLoan(found2at)
			thisloan["match_exception"]=mymatch
	if found:
		#print "Found it!!!"
		#print("Second found")
		try:
			thisloan["url_paid"]=p_response[0][u'data'][u'children'][0][u'data'][u'url']
			thisloan["paid"]=u'Y'
			if p_response[0][u'data'][u'children'][0][u'data'][u'selftext'].lower().find("late")==-1:
				thisloan["schedule"]=u'late'
			elif p_response[0][u'data'][u'children'][0][u'data'][u'selftext'].lower().find("early")==-1:
				thisloan["schedule"]=u'early'
			else:
				thisloan["schedule"]=u'on-time'
			thisloan["deliquent"]=u'N'
			thisloan["actual_date"]=datetime.datetime.utcfromtimestamp(p_response[0][u'data'][u'children'][0][u'data'][u'created'])
			thisloan["paid_header"]=p_response[0][u'data'][u'children'][0][u'data'][u'selftext']
			thisloan["paid_comments"]=list()
			for i in range(len(p_response[0][u'data'][u'children'])):
				if p_response[0][u'data'][u'children'][i][u'data'][u'author'] not in [u'LoansBot',u'AutoModerator']:
					thisloan["paid_comments"].append(p_response[0][u'data'][u'children'][i][u'data'][u'selftext'])
			#if posttype=="LATE":
			#	thisloan["late"]=u'Y'
			#print(mymatch)
			return(thisloan)#writeLoan(thisloan)
		except:
			#Probably the file doesn't exist
			#print "Finding error"
			broken_paids.append(p_url)
	else:
		#print "Finding error"
		broken_paids.append(p_url)
	#print(mymatch)
		