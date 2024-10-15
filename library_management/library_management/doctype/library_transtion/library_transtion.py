# Copyright (c) 2024, Pratik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus

class LibraryTranstion(Document):
	def before_save(self):
		issue_count = frappe.db.count('Library Transtion',{'library_member':self.library_member,'type':'Issue',"article":self.article})
		return_count = frappe.db.count('Library Transtion',{'library_member':self.library_member,'type':'Return',"article":self.article})
		##frappe.msgprint(str(issue_count))
		##frappe.msgprint(str(return_count))

		if issue_count - return_count == 0 and self.type == "Return":
			frappe.throw("Article not issued to member.")
	
	
	def before_submit(self):
		if self.type == "Issue":
			# validate issue.
			self.validate_issue()
			self.validate_maximum_limit()
			article = frappe.get_doc("Article",self.article)
			article.status = "Issued"
			article.save()

		elif self.type == "Return":
			self.validate_return()
			article = frappe.get_doc("Article",self.article)
			article.status = "Available"
			article.save()

	def validate_issue(self):
		# Validate membership
		self.validate_membership()
		article = frappe.get_doc("Article",self.article)

		if article.status == "Issued":
			frappe.throw("Article already issued.")

	def validate_return(self):
		

		article = frappe.get_doc("Article",self.article)

		if article.status == "Available":
			frappe.throw("Article already returned.")
	
	def validate_maximum_limit(self):
		max_articles = frappe.db.get_single_value("Library Settings","maximum_number_of_issued_articles")
		count = frappe.db.count(
			"Library Transtion",
			{
				"library_member":self.library_member,
				"type":"Issue",
				"docstatus":DocStatus.submitted()
			},
		)
		if count > max_articles:
			frappe.throw("Maximum limit reached for issuing article")

	def validate_membership(self):
		valid_membership = frappe.db.exists(
			"Library Membership",
			{
				"library_member" : self.library_member,
				"docstatus": DocStatus.submitted(),
				"from_date":("<",self.date),
				"to_date":(">",self.date),
			},
		
		)

		if not valid_membership:
			frappe.throw("The member does not have valid membership")




