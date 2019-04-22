class CustomBST:
	def __init__(self, p_user="", p_id=""):
		if p_user == "":
			self.__thisuser = ""
		else:
			self.__thisuser = p_user
			self.__left = CustomBST("")
			self.__right = CustomBST("")
			self.__thisids = [p_id]
	
	def push(self, p_user, p_id):
		if self.__thisuser == "":
			self.__thisuser = p_user
			self.__left = CustomBST("")
			self.__right = CustomBST("")
			self.__thisids = [p_id]
		else:
			if self.__thisuser == p_user:
				if p_id not in self.__thisids:
					self.__thisids.append(p_id)
			elif p_user < self.__thisuser:
				self.__left.push(p_user, p_id)
			else:
				self.__right.push(p_user, p_id)
	
	def getids(self, p_user):
		if self.__thisuser == "":
			return list()
		if self.__thisuser == p_user:
			return self.__thisids
		if p_user < self.__thisuser:
			return self.__left.getids(p_user)
		return self.__right.getids(p_user)
	
	def print_all(self):
		if self.__thisuser!="":
			print self.__thisuser
			self.__left.print_all()
			self.__right.print_all()

def read_loan(p_id):
	reader = unicodecsv.reader(open("data/loans/{}.csv".format(p_loan["id"]), 'r'))
	to_return = {rows[0]: rows[1] for rows in reader}
	return to_return

def write_loan(p_loan, defer_index_loader=False):
	global borrower_index
	global lender_index
	if not defer_index_loader:
		try:
			borrower_index = pickle.load(open("borrower_index.dat", 'r'))
		except:
			borrower_index = CustomBST()
		try:
			lender_index=pickle.load(open("lender_index.dat", "r"))
		except:
			lender_index=CustomBST()

	borrower_index.push(p_loan["borrower"], p_loan["id"])
	if p_loan["lender"] != u'NULL':
		lender_index.push(p_loan["lender"], p_loan["id"])
	writer = unicodecsv.writer(open("data/loans/{}.csv".format(p_loan["id"]), "wb"))
	for key, value in p_loan.items():
	   writer.writerow([key, value])
	if not defer_index_loader:
		pickle.dump(borrower_index, open("rborrow/borrower_index.dat", "w"))
		pickle.dump(lender_index, open("rborrow/lender_index.dat", "w"))

def find_loan(lender_list, borrower_list, p_lender=None, p_borrower=None):
	to_return = dict()
	to_return["filename"] = None
	to_return["candidates"] = 0
	if p_borrower is None and p_lender is None:
		#Nothing we can do
		return

	if p_borrower is None:
		for loan in lender_list.getids(p_lender):
			try:
				ws = readLoan(loan)
				if ws["deliquent"] == u'Unknown':
					to_return["filename"] = loan
					to_return["candidates"] += 1
			except:
				pass
		return to_return

	if p_lender is None:
		for loan in borrower_list.getids(p_borrower):
			try:
				ws = readLoan(loan)
				if ws["deliquent"] == u'Unknown':
					to_return["filename"] = loan
					to_return["candidates"] += 1
			except:
				pass
		return to_return

	for loan in lender_list.getids(p_lender):
		try:
			ws=readLoan(loan)
			if ws["deliquent"] == u'Unknown' and ws["borrower"] == p_borrower:
				to_return["filename"] = loan
				to_return["candidates"] += 1
		except:
			pass
	return to_return
