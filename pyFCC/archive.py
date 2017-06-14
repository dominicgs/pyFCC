import requests
from bs4 import BeautifulSoup
import string
import sys
import os
import re


fcc_url = "https://apps.fcc.gov"
product_search_url = "/oetcf/eas/reports/GenericSearchResult.cfm?RequestTimeout=500"

s = requests.Session()

# Perform FCC ID search
def lookup_fcc_id(app_id, product_id, FromRec = 1):
	payload = {
		"application_status" : "",
		"applicant_name" : "",
		"grant_date_from" : "",
		"grant_date_to" : "",
		"grant_comments_label" : "",
		"application_purpose" : "",
		"application_purpose_description" : "",
		"grant_code_1" : "",
		"grant_code_2" : "",
		"grant_code_3" : "",
		"test_firm" : "",
		"equipment_class" : "",
		"equipment_class_description" : "",
		"lower_frequency" : "",
		"upper_frequency" : "",
		"freq_exact_match" : "checked",
		"bandwidth_from" : "",
		"emission_designator" : "",
		"tolerance_from" : "",
		"tolerance_to" : "",
		"tolerance_exact_match" : "checked",
		"power_output_from" : "",
		"power_output_to" : "",
		"power_exact_match" : "checked",
		"rule_part_1" : "",
		"rule_part_2" : "",
		"rule_part_3" : "",
		"rule_part_exact_match" : "checked",
		"product_description" : "",
		"tcb_code" : "",
		"tcb_code_description" : "",
		"tcb_scope" : "",
		"tcb_scope_description" : "",
		"fetchfrom" : "0",
		"calledFromFrame" : "Y",
		"comments" : "",
		"show_records" : "100",
		"grantee_code" : app_id,
		"product_code" : product_id,
		"FromRec" : FromRec
	}
	r = s.post(fcc_url + product_search_url, data=payload)
	print("FCC ID lookup complete")
	return r.text

# format app_id and product_id correctly
def parse_fcc_id(app_id=None, product_id=None):
	if app_id is None:
		return None
	if product_id is None:
		product_id = ''
	if app_id[0] in string.ascii_letters:
		app_len = 3
	elif app_id[0] in string.digits:
		app_len = 5
	else:
		return None

	if len(app_id) > app_len:
		product_id = app_id[app_len:] + product_id
		app_id = app_id[:app_len]
	return (app_id, product_id)

# Parsesearch results page to find "Detail" link
def parse_search_results(html, tupIDdict):
	soup = BeautifulSoup(html, "html.parser")
	rs_tables = soup("table", id="rsTable")
	if len(rs_tables) != 1:
		raise Exception("Error, found %d results tables" % len(rs_tables))
	
	rows = rs_tables[0].find_all("tr") 

	for row in rows:
		links = row.find_all("a", href=re.compile("/oetcf/eas/reports/ViewExhibitReport.cfm\?mode=Exhibits"))
		links = [link['href'] for link in links]
		if len(links) == 0:
			continue
		cols = row.find_all("td")
		ID = cols[11].get_text().strip()
		grantee_code, product_code = parse_fcc_id(ID)
		
		#links[0] = url, cols[11] = full ID, cols[14] = low_freq, cols[15] = high_freq
		product_info = {
			'grantee_code': grantee_code,
			'product_code': product_code,
			'url': links[0],
			'ID': cols[11].get_text().strip(),
			'low_freq': cols[14].get_text().strip(),
			'high_freq': cols[15].get_text().strip(),
		}

		if ID not in tupIDdict:
			tupIDdict[ID] = []
		product_info['version'] = len(tupIDdict[ID]) + 1
		tupIDdict[ID].append(product_info)

	print("Detail link found")
	i = soup.find_all("input", value = "Show Next 100 Rows")

	return tupIDdict, len(i)!=0

# Request details page
def get_attachment_urls(detail_url):
	r = s.get(fcc_url + detail_url)
	soup = BeautifulSoup(r.text, "html.parser")
	rs_tables = soup("table", id="rsTable")

	if len(rs_tables) == 0:
		print("No results available")
		return []
	if len(rs_tables) != 1:
		raise Exception("Error, found %d results tables" % len(rs_tables))

	a_tags = rs_tables[0].find_all("a", href=re.compile("/eas/GetApplicationAttachment.html"))
	links = [(tag.string, tag['href']) for tag in a_tags]

	print("Exhibit links found")
	return links


# Fetch files and pack in to archive
def fetch_and_pack(attachments, dir_name, referer):
	os.makedirs(dir_name)
	for (name, url) in attachments:
		print("Fetching %s" % name)
		r = s.get(fcc_url + url, headers=dict(Referer=referer))

		extension = r.headers['content-type'].split('/')[-1]
		filename = name + '.' + extension
		print("Writing %s" % filename)
		with open(dir_name + '/' + filename, 'wb') as handle:
			for chunk in r.iter_content():
				handle.write(chunk)

def load_next(fcc_id):
	app_id, product_id = parse_fcc_id(fcc_id)
	html_doc = lookup_fcc_id(app_id, product_id)
	productData = {}
	productData, morePages = parse_search_results(html_doc, productData)
	FromRec = 101
	while morePages:
		html_doc = lookup_fcc_id(app_id, product_id, FromRec)
		productData, morePages = parse_search_results(html_doc, productData)
		FromRec += 100
	print(len(productData))

	return productData

