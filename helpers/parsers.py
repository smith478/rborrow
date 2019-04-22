esign="€".decode('utf8')
psign="£".decode('utf8')

nulldate=parser.parse("1/1/1099")
media=["paypal","venmo","google wallet","money gram","simple transfer","chase","etransfer"]
def parse_date(p_str,borrow_date=nulldate,inbody=0):
	default_date=datetime.date.today()
	if borrow_date!=nulldate:
		default_date=borrow_date
	date_set=set()
	if inbody==0:
		try:
			to_return=parser.parse(p_str,default=default_date,fuzzy=False)
		except:
			to_return=u'NULL'
		if to_return==u'NULL':
			for words in p_str.split():
				if words.find("/")!=-1 or words.find("-")!=-1:
					try:
						holdnewdate=parser.parse(words,default=default_date)
						if borrow_date==nulldate or holdnewdate>borrow_date:
							date_set |= {holdnewdate}
					except:
						assert(True)
			if len(date_set)>0:
				return min(date_set)
			else:
				for pairs in nltk.trigrams(nltk.word_tokenize(p_str)):
					try:
						holdnewdate=parser.parse(" ".join(pairs),default=default_date)
						if borrow_date==nulldate or holdnewdate>borrow_date:
							date_set |= {holdnewdate}
					except:
						assert(True)
				if len(date_set)>0:
					return min(date_set)
				else:
					for pairs in nltk.bigrams(nltk.word_tokenize(p_str)):
						try:
							holdnewdate=parser.parse(" ".join(pairs),default=default_date)
							if borrow_date==nulldate or holdnewdate>borrow_date:
								date_set |= {holdnewdate}
						except:
							assert(True)
					if len(date_set)>0:
						return min(date_set)
					else:
						for words in nltk.bigrams(nltk.word_tokenize(p_str)):
							try:
								holdnewdate=parser.parse(words,default=default_date)
								if borrow_date==nulldate or holdnewdate>borrow_date:
									date_set |= {holdnewdate}
							except:
								assert(True)
						if len(date_set)>0:
							return min(date_set)
						else:
							to_return=u'NULL'
			
	else:
		to_return=u'NULL'
	return to_return


def parse_currency(p_str,inbody=0):
	to_return=dict()
	if inbody==0:
		try:
			to_return["currency"]=u'NULL'
			to_return["amount"]=int(float(p_str.lower()))
		except:
			try:
				to_return["currency"]=u'USD'
				to_return["amount"]=int(float(p_str.lower().replace("dollar","").replace("usd","").replace("$","")))
			except:
				try:
					to_return["currency"]=u'EUR'
					to_return["amount"]=int(float(p_str.lower().replace("euro","").replace("eur","").replace(esign,"")))
				except:
					try:
						to_return["currency"]=u'CAN'
						to_return["amount"]=int(float(p_str.lower().replace("dollar","").replace("cdn","").replace("can","").replace("$","")))
					except:
						try:
							to_return["currency"]=u'GBP'
							to_return["amount"]=int(float(p_str.lower().replace("gbp","").replace("pounds","").replace(psign,"")))
						except:
							to_return["currency"]=u'NULL'
							to_return["amount"]=u'NULL'
	else:
		to_return["currency"]=u'NULL'
		to_return["amount"]=u'NULL'
	return to_return

def parse_currency_string(p_str,inbody=0):
	to_return=dict()
	to_return["borrow"]=u'NULL'
	to_return["payback"]=u'NULL'
	to_return["currency"]=u'NULL'
	to_return["source_control"]=0
	hundred_flag=False
	working_str=p_str.replace("+"," ").lower().replace("[req]","")
	if inbody==0:
		# First look for a number or dollar amount in the first word.  In this case, this is the borrowed amount
		first_word_money=parse_currency(working_str.split()[0])
		if first_word_money["amount"]!=u'NULL' and (first_word_money["amount"]>=100 or (first_word_money["amount"]%5==0 and first_word_money["amount"]>=20)):
			to_return["borrow"]=first_word_money["amount"]
			if first_word_money["currency"]!=u'NULL':
				to_return["currency"]=first_word_money["currency"]
			else:
				to_return["currency"]=u'NULL'
				if to_return["currency"]==u'NULL' and (working_str.find("can ")!=-1 or working_str.find("cdn")!=-1):
					to_return["currency"]=u'CAN'
				if to_return["currency"]==u'NULL' and (working_str.find(psign)!=-1 or working_str.find("pound")!=-1 or working_str.find("gbp")!=-1):
					to_return["currency"]=u'GBP'
				if to_return["currency"]==u'NULL' and (working_str.find(esign)!=-1 or working_str.find("eur")!=-1):
					to_return["currency"]=u'EUR'
				if to_return["currency"]==u'NULL' and (working_str.find("$")!=-1 or working_str.find("dollar")!=-1 or working_str.find("gbp")!=-1):
					to_return["currency"]=u'USD'
			# See if you can find the payback in the rest of the title
			to_return["payback"]=u'NULL'
			# Look for a plus sign after all
			if to_return["payback"]==u'NULL' and p_str.find("+")!=1:
				if p_str.replace("[req]","").split()[0].find("+")!=-1:
					get_plus=parse_currency(p_str.replace("[req]","").lower().split()[0].split("+")[1])
					if get_plus["amount"]!=u'NULL' and get_plus["amount"]<to_return["amount"]:
						to_return["payback"]=get_plus["amount"]
						to_return["source_control"]+=51
				else:
					if p_str.replace("[req]","").split()[1].find("+")!=-1:
						get_plus=parse_currency(p_str.replace("[req]","").lower().replace("+","").split()[1])
						if get_plus["amount"]!=u'NULL' and get_plus["amount"]<to_return["amount"]:
							to_return["payback"]=get_plus["amount"]
							to_return["source_control"]+=52
			working_str=" ".join(working_str.split()[1:])
			# Special case that intersest amount is stated
			if to_return["payback"]==u'NULL' and working_str.find("%")!=1 or working_str.find("percent")!=-1:
				backprobe=u'NULL'
				for u in working_str.split():
					if u.find("%")!=-1 or u.find("percent")!=-1:
						if u.find("percent")!=-1:
							to_return["payback"]=backprobe
							to_return["source_control"]+=21
						else:
							try:
								to_return["payback"]=(1.0+float(u.replace("%",""))/100.0)*to_return["borrow"]
								to_return["source_control"]+=1
							except:
								if to_return["payback"]==u'NULL':
									# Try previous word?
									to_return["payback"]=backprobe
									to_return["source_control"]+=2
					else:
						try:
							backprobe=(1.0+float(u.replace("%",""))/100.0)*to_return["borrow"]
						except:
							backprobe=u'NULL'
			# Try to find stated interest
			if to_return["payback"]==u'NULL' and working_str.find("interest")!=-1:
				backprobe=u'NULL'
				for u in working_str.split():
					if u.find("interest")!=-1:
						to_return["payback"]=backprobe
						to_return["source_control"]+=53
					else:
						backprobe=parse_currency(u)["amount"]
			# First look to see if there's a single candidate
			if to_return["payback"]==u'NULL' and (to_return["currency"]==u'USD' or to_return["currency"]==u'CAN' or to_return["currency"]==u'NULL') and working_str.count("$")==1:
				# Probe intended to deal with "$ 500" case where the extra space is there.
				probe=False
				for u in working_str.split():
					if probe:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=3
						probe=False
					if u.find("$")!=-1:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=4
						if to_return["payback"]==u'NULL':
							# Try next word?
							probe=True
			if to_return["payback"]==u'NULL' and (to_return["currency"]==u'EUR' or to_return["currency"]==u'NULL') and working_str.count(esign)==1:
				# Probe intended to deal with "$ 500" case where the extra space is there.
				probe=False
				for u in working_str.split():
					if probe:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=5
						probe=False
					if u.find(esign)!=-1:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=6
						if to_return["payback"]==u'NULL':
							# Try next word?
							probe=True
			if to_return["payback"]==u'NULL' and (to_return["currency"]==u'GBP' or to_return["currency"]==u'NULL') and working_str.count(psign)==1:
				# Probe intended to deal with "$ 500" case where the extra space is there.
				probe=False
				for u in working_str.split():
					if probe:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=7
						probe=False
					if u.find(esign)!=-1:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=8
						if to_return["payback"]==u'NULL':
							# Try next word?
							probe=True
			# We'll continue down this path, but this time looking for words.  This time we have to probe backwards though, so it's difficult.
			# First we need to trim to the first word if it should be attached to the removed word.
			second_word=working_str.split()[0]
			if parse_currency(second_word)["amount"]==u'NULL' and (second_word.find("dollar")!=-1 or second_word.find("pound")!=-1 or second_word.find("euro")!=-1 or second_word.find("can ")!=-1 or second_word.find("cdn")!=-1 or second_word.find("eur")!=-1 or second_word.find("gbp")!=-1):
				working_str=" ".join(working_str.split()[1:])
			backprobe=u'NULL'
			if to_return["payback"]==u'NULL' and (to_return["currency"]==u'USD' or to_return["currency"]==u'CAN' or to_return["currency"]==u'NULL') and working_str.count("dollar")==1:
				for u in working_str.split():
					if u.find("dollar")!=-1:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=9
						if to_return["payback"]==u'NULL':
							# Try previous word?
							to_return["payback"]=backprobe
							to_return["source_control"]+=10
					else:
						backprobe=parse_currency(u)["amount"]
			if to_return["payback"]==u'NULL' and (to_return["currency"]==u'USD' or to_return["currency"]==u'NULL') and working_str.count("usd")==1:
				for u in working_str.split():
					if u.find("usd")!=-1:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=11
						if to_return["payback"]==u'NULL':
							# Try previous word?
							to_return["payback"]=backprobe
							to_return["source_control"]+=12
					else:
						backprobe=parse_currency(u)["amount"]
			if to_return["payback"]==u'NULL' and (to_return["currency"]==u'CAN' or to_return["currency"]==u'NULL') and working_str.count("can ")==1:
				for u in working_str.split():
					if u.find("can ")!=-1 or u.find("cdn")!=-1:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=13
						if to_return["payback"]==u'NULL':
							# Try previous word?
							to_return["payback"]=backprobe
							to_return["source_control"]+=14
					else:
						backprobe=parse_currency(u)["amount"]
			if to_return["payback"]==u'NULL' and (to_return["currency"]==u'EUR' or to_return["currency"]==u'NULL') and working_str.count("eur")==1:
				for u in working_str.split():
					if u.find("eur")!=-1:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=15
						if to_return["payback"]==u'NULL':
							# Try previous word?
							to_return["payback"]=backprobe
							to_return["source_control"]+=16
					else:
						backprobe=parse_currency(u)["amount"]
			if to_return["payback"]==u'NULL' and (to_return["currency"]==u'GBP' or to_return["currency"]==u'NULL') and working_str.count("gbp")+working_str.count("pound")==1:
				for u in working_str.split():
					if u.find("gbp")!=-1 or u.find("pound")!=-1:
						to_return["payback"]=parse_currency(u)["amount"]
						to_return["source_control"]+=17
						if to_return["payback"]==u'NULL':
							# Try previous word?
							to_return["payback"]=backprobe
							to_return["source_control"]+=18
					else:
						backprobe=parse_currency(u)["amount"]
			# The next round of looking for stuff involves just trying to find numbers
			# Numbers can be dates or some other nonsense, so you have to decide what's a reasonable region.
			if to_return["payback"]==u'NULL':
				candidates=list()
				for u in working_str.split():
					try:
						mynum=int(float(u))
						if mynum>to_return["borrow"] and mynum<=1.5*to_return["borrow"] and mynum%5==0:
							candidates |= {mynum}
					except:
						# Do nothing
						assert(True)
				if len(candidates)==1:
					to_return["payback"]=candidates[0]
					to_return["source_control"]+=19
				elif len(candidates)==0:
					candidates=list()
					for u in working_str.split():
						try:
							mynum=int(float(u))
							# Probably too broad, but just trying to fill in some guess...
							if mynum>to_return["borrow"] and mynum<=2*to_return["borrow"]:
								candidates |= {mynum}
						except:
							# Do nothing
							assert(True)
					if len(candidates)==1:
						to_return["payback"]=candidates[0]
						to_return["source_control"]+=20
		else:
			# Need to handle the interest case separately...
			if working_str.find("%")!=-1 or working_str.find("percent")!=-1:
				#Just shove some currency logic in here willy nilly because I'm getting lazy.
				if to_return["currency"]==u'NULL':
					# If one of these things is in there, then it must be these, right?
					if to_return["currency"]==u'NULL' and working_str.find("usd")!=-1:
						to_return["currency"]=u'USD'
					if to_return["currency"]==u'NULL' and (working_str.find("can ")!=-1 or working_str.find("cdn")!=-1):
						to_return["currency"]=u'CAN'
					if to_return["currency"]==u'NULL' and (working_str.find(esign)!=-1 or working_str.find("eur")!=-1):
						to_return["currency"]=u'EUR'
					if to_return["currency"]==u'NULL' and (working_str.find(psign)!=-1 or working_str.find("gbp")!=-1 or working_str.find("pound")!=-1):
						to_return["currency"]=u'GBP'
					for u in working_str.split():
						if to_return["currency"]==u'NULL':
							to_return["currency"]=parse_currency(u)["currency"]
					if to_return["currency"]==u'NULL' and (working_str.find("$")!=-1 or working_str.find("dollar")):
						to_return["currency"]=u'USD'
				
				hold_percent=-1.0
				delete_it=""
				backprobe=u'NULL'
				for u in working_str.split():
					if u.find("%")!=-1 or u.find("percent")!=-1:
						if u.find("percent")!=-1:
							hold_percent=backprobe
						else:
							try:
								hold_percent=(1.0+float(u.replace("%",""))/100.0)
								delete_it=u
							except:
								if hold_percent==-1.0:
									# Try previous word?
									hold_percent=backprobe
					else:
						try:
							backprobe=(1.0+float(u.replace("%",""))/100.0)
							delete_it=u
						except:
							backprobe=u'NULL'
							delete_it=""
				if hold_percent==-1.0:
					#Percent logic was a big mistake
					#Proceed with usual logic
					hundred_flag=True
					to_return["source_control"]+=100
				else:
					#Remove it from the string
					working_str=working_str.replace(delete_it,"")
					#Now try to find a single number that we think will be the amount borrowed.
					candidates=set()
					for u in working_str.split():
						try:
							hold_can=int(parse_currency(u)["amount"])
							#Look for things with dollar signs and shit.
							if hold_can>=20 and hold_can%5==0 and parse_currency(u)["currency"]!=u'NULL':
								candidates |= {hold_can}
						except:
							# Do nothing
							assert(True)
					# Too many numbers exist
					if len(candidates)>1:
						alt_candidates=set()
						for u in working_str.split():
							try:
								hold_can=int(parse_currency(u)["amount"])
								if hold_can>=100 and hold_can%5==0 and parse_currency(u)["currency"]!=u'NULL':
									candidates |= {hold_can}
							except:
								# Do nothing
								assert(True)
						# If cutting down is okay, then do so
						if len(alt_candidates)>=1:
							candidates=alt_candidates
						if len(candidates)>1:
							alt_candidates=set()
							for u in working_str.split():
								try:
									hold_can=int(parse_currency(u)["amount"])
									if hold_can>=100 and hold_can%25==0 and parse_currency(u)["currency"]!=u'NULL':
										candidates |= {hold_can}
								except:
									# Do nothing
									assert(True)
							# If cutting down is okay, then do so
							if len(alt_candidates)>=1:
								candidates=alt_candidates
						if len(candidates)>1:
							#Can't figure anything out
							to_return["borrow"]=u'NULL'
							to_return["payback"]=u'NULL'
							to_return["source_control"]+=30
						else:
							to_return["borrow"]=min(candidates)
							to_return["payback"]=to_return["borrow"]*hold_percent
							to_return["source_control"]+=31
					# Try relaxing the requirement that "$" need be present.  Mostly repeated
					else:
						#Now try to find a single number that we think will be the amount borrowed.
						candidates=set()
						for u in working_str.split():
							try:
								hold_can=int(parse_currency(u)["amount"])
								#Look for things with dollar signs and shit.
								if hold_can>=20 and hold_can%5==0:
									candidates |= {hold_can}
							except:
								# Do nothing
								assert(True)
						# Too many numbers exist
						if len(candidates)>1:
							alt_candidates=set()
							for u in working_str.split():
								try:
									hold_can=int(parse_currency(u)["amount"])
									if hold_can>=100 and hold_can%5==0:
										candidates |= {hold_can}
								except:
									# Do nothing
									assert(True)
							# If cutting down is okay, then do so
							if len(alt_candidates)>=1:
								candidates=alt_candidates
							if len(candidates)>1:
								alt_candidates=set()
								for u in working_str.split():
									try:
										hold_can=int(parse_currency(u)["amount"])
										if hold_can>=100 and hold_can%25==0:
											candidates |= {hold_can}
									except:
										# Do nothing
										assert(True)
								# If cutting down is okay, then do so
								if len(alt_candidates)>=1:
									candidates=alt_candidates
							if len(candidates)>1:
								#Can't figure anything out
								to_return["borrow"]=u'NULL'
								to_return["payback"]=u'NULL'
								to_return["source_control"]+=32
							else:
								to_return["borrow"]=min(candidates)
								to_return["payback"]=to_return["borrow"]*hold_percent
								to_return["source_control"]+=33
						elif len(candidates)==1:
							to_return["borrow"]=min(candidates)
							to_return["payback"]=to_return["borrow"]*hold_percent
							to_return["source_control"]+=35
						else:
							#Can't figure anything out
							to_return["borrow"]=u'NULL'
							to_return["payback"]=u'NULL'
							to_return["source_control"]+=34
			if (working_str.find("%")==-1 and working_str.find("percent")==-1) or hundred_flag:
				# Get all the money amount of 
				candidates=set()
				for u in working_str.split():
					try:
						hold_can=int(parse_currency(u)["amount"])
						#Look for things with dollar signs and shit.
						if hold_can>=20 and hold_can%5==0 and parse_currency(u)["currency"]!=u'NULL':
							candidates |= {hold_can}
					except:
						# Do nothing
						assert(True)
				# Too many numbers exist
				if len(candidates)>2:
					alt_candidates=set()
					for u in working_str.split():
						try:
							hold_can=int(parse_currency(u)["amount"])
							if hold_can>=100 and hold_can%5==0 and parse_currency(u)["currency"]!=u'NULL':
								alt_candidates |= {hold_can}
						except:
							# Do nothing
							assert(True)
					# If cutting down is okay, then do so
					if len(alt_candidates)>=2:
						candidates=alt_candidates
					# Find the two values that are closest to each other.
					# We're going to repeatedly remove the end point that is further away
					while len(candidates)>2:
						min1=min(candidates)
						min2=min([x for x in candidates if x!=min1])
						max1=min(candidates)
						max2=min([x for x in candidates if x!=max1])
						if min2-min1<max2-max2:
							candidates=set([x for x in candidates if x!=max1])
						else:
							candidates=set([x for x in candidates if x!=min1])
					# Try to figure out what the currency is
					to_return["currency"]=u'NULL'
					for u in working_str.split():
						if to_return["currency"]==u'NULL':
							try:
								if int(parse_currency(u)["amount"]) in candidates:
									to_return["currency"]=parse_currency(u)["currency"]
							except:
								# Do nothing
								assert(True)
					if to_return["currency"]==u'NULL':
						# If one of these things is in there, then it must be these, right?
						if to_return["currency"]==u'NULL' and working_str.find("usd")!=-1:
							to_return["currency"]=u'USD'
						if to_return["currency"]==u'NULL' and (working_str.find("can ")!=-1 or working_str.find("cdn")!=-1):
							to_return["currency"]=u'CAN'
						if to_return["currency"]==u'NULL' and (working_str.find(esign)!=-1 or working_str.find("eur")!=-1):
							to_return["currency"]=u'EUR'
						if to_return["currency"]==u'NULL' and (working_str.find(psign)!=-1 or working_str.find("gbp")!=-1):
							to_return["currency"]=u'GBP'
						for u in working_str.split():
							if to_return["currency"]==u'NULL':
								to_return["currency"]=parse_currency(u)["currency"]
						if to_return["currency"]==u'NULL' and (working_str.find("$")!=-1 or working_str.find("dollar")!=-1):
							to_return["currency"]=u'USD'
					# Set lower number to the borrowed amt
					to_return["borrow"]=min(candidates)
					to_return["payback"]=max(candidates)
					to_return["source_control"]+=22
				elif len(candidates)==1:
					# Try to figure out what the currency is
					to_return["currency"]=u'NULL'
					for u in working_str.split():
						if to_return["currency"]==u'NULL':
							try:
								if int(parse_currency(u)["amount"]) in candidates:
									to_return["currency"]=parse_currency(u)["currency"]
							except:
								# Do nothing
								assert(True)
					if to_return["currency"]==u'NULL':
						# If one of these things is in there, then it must be these, right?
						if to_return["currency"]==u'NULL' and working_str.find("usd")!=-1:
							to_return["currency"]=u'USD'
						if to_return["currency"]==u'NULL' and (working_str.find("can ")!=-1 or working_str.find("cdn")!=-1):
							to_return["currency"]=u'CAN'
						if to_return["currency"]==u'NULL' and (working_str.find(esign)!=-1 or working_str.find("eur")!=-1):
							to_return["currency"]=u'EUR'
						if to_return["currency"]==u'NULL' and (working_str.find(psign)!=-1 or working_str.find("gbp")!=-1):
							to_return["currency"]=u'GBP'
						for u in working_str.split():
							if to_return["currency"]==u'NULL':
								to_return["currency"]=parse_currency(u)["currency"]
						if to_return["currency"]==u'NULL' and (working_str.find("$")!=-1 or working_str.find("dollar")!=-1):
							to_return["currency"]=u'USD'
					# Set lower number to the borrowed amt
					to_return["borrow"]=min(candidates)
					to_return["payback"]=u'NULL'
					to_return["source_control"]+=23
					# Try my damn'd'est to find a payback value, by looking at all numbers as a whole.
					# Repeated, but modified code.
					if True: # For asethetic reasons, I wanted this next part indented.
						for u in working_str.split():
							try:
								hold_can=int(parse_currency(u)["amount"])
								#Look for things with dollar signs and shit.
								if hold_can>=20 and hold_can%5==0 and parse_currency(u)["currency"]!=u'NULL':
									candidates |= {hold_can}
							except:
								# Do nothing
								assert(True)
						# Too many numbers exist
						if len(candidates)>2:
							alt_candidates=set()
							for u in working_str.split():
								try:
									hold_can=int(parse_currency(u)["amount"])
									if hold_can>=100 and hold_can%5==0:
										candidates |= {hold_can}
								except:
									# Do nothing
									assert(True)
							# If cutting down is okay, then do so
							if len(alt_candidates)>=2:
								candidates=alt_candidates
							# Find the two values that are closest to each other.
							# We're going to repeatedly remove the end point that is further away
							while len(candidates)>2:
								min1=min(candidates)
								min2=min([x for x in candidates if x!=min1])
								max1=min(candidates)
								max2=min([x for x in candidates if x!=max1])
								if min1==to_return["borrow"]:
									candidates=set([x for x in candidates if x!=max1])
								elif max1==to_return["borrow"]:
									candidates=set([x for x in candidates if x!=min1])
								elif min2-min1<max2-max2:
									candidates=set([x for x in candidates if x!=max1])
								else:
									candidates=set([x for x in candidates if x!=min1])
							# Set lower number to the borrowed amt
							for xyz in candidates:
								if xyz!=to_return["borrow"]:
									to_return["payback"]=xyz
							if to_return["borrow"]>to_return["payback"]:
								temp=to_return["borrow"]
								to_return["borrow"]=to_return["payback"]
								to_return["payback"]=temp
							to_return["source_control"]+=26
				# Nothing with dollar signs or anything. Start to consider all numbers.
				# Repeated code
				else:
					candidates=set()
					for u in working_str.split():
						try:
							hold_can=int(parse_currency(u)["amount"])
							if hold_can>=20 and hold_can%5==0:			# This is the only piece to change from above
								candidates |= {hold_can}
						except:
							# Do nothing
							assert(True)
					# Too many numbers exist
					if len(candidates)>2:
						alt_candidates=set()
						for u in working_str.split():
							try:
								hold_can=int(parse_currency(u)["amount"])
								if hold_can>=100 and hold_can%5==0:
									alt_candidates|={hold_can}
							except:
								# Do nothing
								assert(True)
						# If cutting down is okay, then do so
						if len(alt_candidates)>=2:
							candidates=alt_candidates
						# Find the two values that are closest to each other.
						# We're going to repeatedly remove the end point that is further away
						while len(candidates)>2:
							min1=min(candidates)
							min2=min([x for x in candidates if x!=min1])
							max1=min(candidates)
							max2=min([x for x in candidates if x!=max1])
							if min2-min1<max2-max2:
								candidates=set([x for x in candidates if x!=max1])
							else:
								candidates=set([x for x in candidates if x!=min1])
						# Try to figure out what the currency is
						to_return["currency"]=u'NULL'
						for u in working_str.split():
							if to_return["currency"]==u'NULL':
								try:
									if int(parse_currency(u)["amount"]) in candidates:
										to_return["currency"]=parse_currency(u)["currency"]
								except:
									# Do nothing
									assert(True)
						if to_return["currency"]==u'NULL':
							# If one of these things is in there, then it must be these, right?
							if to_return["currency"]==u'NULL' and working_str.find("usd")!=-1:
								to_return["currency"]=u'USD'
							if to_return["currency"]==u'NULL' and (working_str.find("can ")!=-1 or working_str.find("cdn")!=-1):
								to_return["currency"]=u'CAN'
							if to_return["currency"]==u'NULL' and (working_str.find(esign)!=-1 or working_str.find("eur")!=-1):
								to_return["currency"]=u'EUR'
							if to_return["currency"]==u'NULL' and (working_str.find(psign)!=-1 or working_str.find("gbp")!=-1 or working_str.find("pound")!=-1):
								to_return["currency"]=u'GBP'
							for u in working_str.split():
								if to_return["currency"]==u'NULL':
									to_return["currency"]=parse_currency(u)["currency"]
							if to_return["currency"]==u'NULL' and (working_str.find("$")!=-1 or working_str.find("dollar")):
								to_return["currency"]=u'USD'
						# Set lower number to the borrowed amt
						to_return["borrow"]=min(candidates)
						to_return["payback"]=max(candidates)
						to_return["source_control"]+=24
					elif len(candidates)==1:
						# Try to figure out what the currency is
						to_return["currency"]=u'NULL'
						for u in working_str.split():
							if to_return["currency"]==u'NULL':
								try:
									if int(parse_currency(u)["amount"]) in candidates:
										to_return["currency"]=parse_currency(u)["currency"]
								except:
									# Do nothing
									assert(True)
						if to_return["currency"]==u'NULL':
							# If one of these things is in there, then it must be these, right?
							if to_return["currency"]==u'NULL' and working_str.find("usd")!=-1:
								to_return["currency"]=u'USD'
							if to_return["currency"]==u'NULL' and (working_str.find("can ")!=-1 or working_str.find("cdn")!=-1):
								to_return["currency"]=u'CAN'
							if to_return["currency"]==u'NULL' and (working_str.find(esign)!=-1 or working_str.find("eur")!=-1):
								to_return["currency"]=u'EUR'
							if to_return["currency"]==u'NULL' and (working_str.find(psign)!=-1 or working_str.find("gbp")!=-1 or working_str.find("pound")!=-1):
								to_return["currency"]=u'GBP'
							for u in working_str.split():
								if to_return["currency"]==u'NULL':
									to_return["currency"]=parse_currency(u)["currency"]
							if to_return["currency"]==u'NULL' and (working_str.find("$")!=-1 or working_str.find("dollar")):
								to_return["currency"]=u'USD'
						# Set lower number to the borrowed amt
						to_return["borrow"]=min(candidates)
						to_return["payback"]=u'NULL'
						to_return["source_control"]+=25
	else:
		to_return["borrow"]=u'NULL'
		to_return["payback"]=u'NULL'
		to_return["currency"]=u'NULL'
		to_return["source_countrol"]=999
	return to_return
