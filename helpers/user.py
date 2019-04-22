
class User:
	def __init__(self, name):
		self.name = name
		self.commentList = []
		self.tenpage=False

	def addComment(self, newComment):
		self.commentList.append(newComment)

	def display(self):
		for i in self.commentList:
			i.display()

	def stats(self,enddate):
		toReturn=dict()
		allSubs = set()
		allClusters = set()
		toReturn["wordsToLiveBy"]=""
		ifuck=0
		for cfuck in self.commentList:
			ifuck+=1
			if ifuck==7:
				toReturn["wordsToLiveBy"]=cfuck.contents
		toReturn["noAll"]=0
		toReturn["karmaAll"]=0
		toReturn["no_cluster_OTHER"]=0
		toReturn["karma_cluster_OTHER"]=0
		for c in self.commentList:
			if c.date<=enddate:
				toReturn["startdate"]=c.date
				toReturn["noAll"]+=1
				toReturn["karmaAll"]+=c.ups
				if c.subreddit not in allSubs and c.subreddit in my200_2:
					allSubs |= {c.subreddit}
					#toReturn["no"+c.subreddit]=0
					#toReturn["karma"+c.subreddit]=0
				if c.subreddit in cluster_dict.keys():
					if cluster_dict[c.subreddit] not in allClusters and c.subreddit in my200_2:
						allClusters |= {cluster_dict[c.subreddit]}
						toReturn["no_cluster_"+cluster_dict[c.subreddit]]=0
						toReturn["karma_cluster_"+cluster_dict[c.subreddit]]=0
					if c.subreddit in my200_2:
						#toReturn["no"+c.subreddit]+=1
						#toReturn["karma"+c.subreddit]+=c.ups
						toReturn["no_cluster_"+cluster_dict[c.subreddit]]+=1
						toReturn["karma_cluster_"+cluster_dict[c.subreddit]]+=c.ups
				else:
					if c.subreddit in my200_2:
						#toReturn["no"+c.subreddit]+=1
						#toReturn["karma"+c.subreddit]+=c.ups
						toReturn["no_cluster_OTHER"]+=1
						toReturn["karma_cluster_OTHER"]+=c.ups
		#for d in allSubs:
		#	toReturn["prop_no"+d]=toReturn["no"+d]/toReturn["noAll"]
		#	toReturn["prop_karma"+d]=toReturn["karma"+d]/toReturn["karmaAll"]
		for d in allClusters:
			toReturn["prop_no_cluster_"+d]=toReturn["no_cluster_"+d]*1.0/toReturn["noAll"]
			toReturn["prop_karma_cluster_"+d]=toReturn["karma_cluster_"+d]*1.0/toReturn["karmaAll"]
		if toReturn["noAll"]>0 and (enddate-toReturn["startdate"]).days>0:
			toReturn["postsPerDay"]=toReturn["noAll"]/(enddate-toReturn["startdate"]).days
		else:
			toReturn["postsPerDay"]=0.0
		toReturn["avg_comment_length"]=np.mean([x.chars for x in self.commentList])
		return toReturn
	
	def settenpage(self):
		self.tenpage=True

class Comment:
	def __init__(self, id, ups, downs, chars, subreddit, date, contents):
		self.id = id
		self.ups = ups
		self.downs = downs
		self.chars = chars
		self.subreddit = subreddit
		self.date = date
		self.contents = contents

	def display(self):
		print("#",self.id)
		print("Subreddit:",self.subreddit)
		print("Total chars:",self.chars)
		print("Ups/Downs:",self.ups,self.downs)

def retrieve_comments(username):
	""" retrieves comments and returns User object containing Comment objects """ 
	print("\nWorking")
	url = 'http://www.reddit.com/user/'+username+'/comments/.json?limit=100'
	user = User(username)
	# perform initial api request and convert to JSON dictionary
	r = requests.get(url, headers=hdr)
	commentSet = r.json()
	while len(commentSet['data']['children']) > 0:
		sys.stdout.flush()
		i = 0
		# process the current set of comments
		for c in commentSet['data']['children']:
			id = c['data']['id']
			ups = int(c['data']['ups'])
			downs = int(c['data']['downs'])
			chars = len(c['data']['body'])
			subreddit = c['data']['subreddit']
			date = datetime.datetime.utcfromtimestamp(c["data"]["created"])
			contents = ""
			i += 1
			if i==7:
				contents = c['data']['body']
			user.addComment(Comment(id, ups, downs, chars, subreddit, date, contents))
		# get the id of the last comment in the set
		lastId = commentSet['data']['children'][-1]['data']['id']
		#print lastId
		# modify the url and retrieve the next set of comments
		r = requests.get(url+"&after=t1_"+lastId, headers=hdr)
		commentSet = r.json()
	return user


def retrieve_about(username):
	""" retrieves comments and returns User object containing Comment objects """ 
	print("\nWorking")
	url = 'http://www.reddit.com/user/'+username+'/about.json'
	r = requests.get(url, headers=hdr)
	aboutSet = r.json()
	to_return=dict()
	to_return["z_age"]=(datetime.datetime.today()-datetime.datetime.utcfromtimestamp(aboutSet['data']['created'])).days
	to_return["z_isgold"]=aboutSet['data']['is_gold']
	to_return["z_verified_email"]=aboutSet['data']['has_verified_email']
	to_return["z_comment_karma"]=aboutSet['data']['comment_karma']
	to_return["z_link_karma"]=aboutSet['data']['link_karma']
	return to_return
