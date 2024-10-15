# Copyright (c) 2024, Pratik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus
import frappe.utils

class LibraryMembership(Document):
	def before_submit(self):
		exist = frappe.db.exists(
			"Library Membership",
			{
				"library_member": self.library_member,
				"docstatus": DocStatus.submitted(),
				# check membership end date to later than start date
				"to_date": (">",self.from_date),
			},
			
		)

		if exist:
			frappe.throw("There is an active membership.")
		
		loan_period = frappe.db.get_single_value("Library Settings","loan_period")
		self.to_date = frappe.utils.add_days(self.from_date,loan_period or 30)
