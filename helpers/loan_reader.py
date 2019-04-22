import numpy as np
import dateutil.parser as parser
from users import *

def parse_loan(unparsed_loan, cluster_dict, botlist_df):
	loan = dict()
	loan["interest"] = None
	loan["payback"] = None
	loan["borrow"] = None
	loan["id"] = unparsed_loan["id"]
	if "match_exception" in unparsed_loan:
		loan["match_exception"] = unparsed_loan["match_exception"]
	loan["paid_url"] = unparsed_loan["url_paid"]
	loan["late"] = unparsed_loan["late"]
	loan["request_date"] = unparsed_loan["request_date"]
	loan["medium"] = unparsed_loan["medium"]
	loan["weekday"] = unparsed_loan["weekday"]
	loan["location_state"] = unparsed_loan["location_state"]
	loan["hour"] = unparsed_loan["hour"]
	loan["link"] = "hyperlink(\"https://www.reddit.com/r/borrow/comments/{}/\")".format(unparsed_loan["id"])
	loan["currency"] = unparsed_loan["currency"]
	loan["source_control"] = unparsed_loan["source_control"]
	if unparsed_loan["amount"] != u'NULL':
		loan["borrow"] = unparsed_loan["amount"]
		if unparsed_loan["payback_amount"] != u'Unknown':
			loan["payback"] = unparsed_loan["payback_amount"]
			if loan["payback"] == u'NULL' or loan["borrow"] == u'NULL' or float(loan["borrow"]) == 0:
				loan["interest"] = 0
			else:
				try:
					loan["interest"] = float(loan["payback"]) * 1.0 / float(loan["borrow"])
				except:
					loan["interest"] = 0
	if unparsed_loan["target_date"] != u'NULL' and unparsed_loan["request_date"] != u'NULL':
		try:
			loan["length"] = (parser.parse(unparsed_loan["target_date"]) - parser.parse(unparsed_loan["request_date"])).days / 365.0
		except:
			loan["length"] = (unparsed_loan["target_date"] - unparsed_loan["request_date"]).days / 365.0
		if loan["interest"] != "Unknown" and loan["length"] != 0:
			unparsed_loan["apy"] = np.power(loan["interest"], 1.0 / loan["length"])

	loan["hist_P"] = 0
	loan["hist_PY"] = 0
	loan["hist_U"] = 0
	loan["hist_UY"] = 0
	loan["hist_N"] = 0
	loan["hist_D"] = 0
	loan["hist_X"] = 0
	loan["hist_Y"] = 0
	loan["hist_E"] = 0
	loan["hist_issue"] = 1
	for i in borrower_index.getids(unparsed_loan["borrower"]):
		if i == unparsed_loan["id"]:
			loan["hist_issue"] = 0
		elif loan["hist_issue"] == 1:
			histfile = readLoan(i)
			if histfile["request_date"] < str(loan["request_date"]):
				if histfile["paid"] == "Y":
					if histfile["deliquent"] == "Y":
						loan["hist_E"] += 1
					elif histfile["request_filled_fromflair"] == "N":
						loan["hist_PY"] += 1
					else:
						loan["hist_P"] += 1
				elif histfile["deliquent"] == "Y":
					if histfile["request_filled_fromflair"] == "N":
						loan["hist_UY"] += 1
					else:
						loan["hist_U"] += 1
				else:
					if histfile["request_filled_fromflair"] == "N":
						loan["hist_Y"] += 1
					elif histfile["due"] == "Y":
						loan["hist_D"] += 1
					elif histfile["due"] == "N":
						loan["hist_N"] += 1
					else:
						loan["hist_X"] += 1
	
	#Try to learn stuff about the borrower
	try:
		thisborrower = retrieve_comments(unparsed_loan["borrower"])
		thisborrower_head = retrieve_about(unparsed_loan["borrower"])
		thisstats = thisborrower.stats(datetime.datetime.utcfromtimestamp(float(unparsed_loan["timestamp"])))
		for k, v in thisstats.items():
			loan[k] = v
		for k, v in thisborrower_head.items():
			loan[k] = v
	except:
		pass
	
	#Check against bot list.
	bot_id = unparsed_loan["id"]
	for _, row in botlist_df:
		if row["Loan ID"] == bot_id:
			loan["bot_found"] = 1
			loan["bot_id"] = row["ID"]
			loan["bot_principal"] = row["Principal"]
	else:
		loan["bot_found"] = 0
	
	# NULL out error values
	if loan["payback"] >= 2016 and loan["payback"] <= 2018:
		loan["payback"] = -1
	#These values are so often errors, maybe it's best to just say that our model won't work on sub-par loans
	if loan["payback"] != -1 and loan["borrow"] != -1 and loan["payback"] < loan["borrow"] * 0.99:
		loan["payback"] = -1
		loan["borrow"] = -1
	#Too highly-leveraged
	if loan["payback"] != -1 and loan["borrow"] != -1 and loan["payback"] >= 1000:
		loan["payback"] = -1
		loan["borrow"] = -1
	if loan["payback"] != -1 and loan["borrow"] != -1 and loan["borrow"] >= 1000:
		loan["payback"] = -1
		loan["borrow"] = -1
	if loan["interest"] == 0.0:
		loan["interest"] = -1
	if loan["interest"] == 1.0:
		loan["interest"] = -1
	if loan["interest"] != -1 and loan["interest"] < 1.0:
		loan["interest"] += 1.0
	
	# Look through clusters
	for i in range(1, len(cluster_dict.keys())):
		loan["no"+str(i)] = 0
		loan["karma"+str(i)] = 0
		for j in cluster_dict.keys():
			if cluster_dict[j] == str(i) and "no"+j in loan.keys():
				loan["no"+str(i)] += loan["no"+j]
				loan["karma"+str(i)] += loan["karma"+j]

	return loan