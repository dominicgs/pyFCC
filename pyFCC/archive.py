import requests
from bs4 import BeautifulSoup
import string
import sys
import os
import re


fcc_url = "https://apps.fcc.gov"
product_search_url = "/oetcf/eas/reports/GenericSearchResult.cfm?RequestTimeout=500"

s = requests.Session()

# Perform FCC id search
def lookup_fccid(appid, productid, FromRec = 1):
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
		#if soup.text = <input class="button-content" name = "next_value" value="show Next 25 Rows"
		"grantee_code" : appid,
		"product_code" : productid,
		"FromRec" : FromRec
	}
	r = s.post(fcc_url + product_search_url, data=payload)
	print("FCC id lookup complete")
	return r.text

# Try to format appid and productid correctly
def parse_fccid(appid=None, productid=None):
	if appid is None:
		return None
	if productid is None:
		productid = ''
	if appid[0] in string.ascii_letters:
		app_len = 3
	elif appid[0] in string.digits:
		app_len = 5
	else:
		return None

	if len(appid) > app_len:
		productid = appid[app_len:] + productid
		appid = appid[:app_len]
	return (appid, productid)

# Parsesearch results page to find "Detail" link
def parse_search_results(html, tupIDdict):
	soup = BeautifulSoup(html, "html.parser")
	#print(html.prettify())
	rs_tables = soup("table", id="rsTable")
	if len(rs_tables) != 1:
		raise Exception("Error, found %d results tables" % len(rs_tables))
	#print("Found %d results" % len(links))
	rows = rs_tables[0].find_all("tr") # get all of the rows in the table
	return_value = []
	#tupIDdict = {}

	for row in rows:
		links = row.find_all("a", href=re.compile("/oetcf/eas/reports/ViewExhibitReport.cfm\?mode=Exhibits"))
		links = [link['href'] for link in links]
		if len(links) == 0:
			continue
		cols = row.find_all("td")
		lot = (links[0], cols[11].get_text().strip(), cols[14].get_text().strip(), cols[15].get_text().strip())
		return_value.append(lot)
		FullfccID = lot[1]
		if FullfccID not in tupIDdict:
			tupIDdict[FullfccID] = []
		tupIDdict[FullfccID].append(lot)
		print(lot)

	# this line happens in main
	#appid, productid = parse_fccid(FullfccID)
	
	print("Detail link found")
	i = soup.find_all(href=re.compile('form action = "/oetcf/eas/reports/GenericSearchResult.cfm?RequestTimeout=500" method="post" name="next_result"'))

	return tupIDdict, len(i)!=0

# Request details page
def get_attachment_urls(detail_url):
	r = s.get(fcc_url + detail_url)
	soup = BeautifulSoup(r.text, "html.parser")

	rs_tables = soup("table", id="rsTable")
	if len(rs_tables) != 1:
		#print(detail_url)
		raise Exception("Error, found %d results tables" % len(rs_tables))

	a_tags = rs_tables[0].find_all("a", href=re.compile("/eas/GetApplicationAttachment.html"))
	links = [(tag.string, tag['href']) for tag in a_tags]

	print("Exhibit links found")
	return links


# Fetch files and pack in to archive
def fetch_and_pack(attachments, dirname, referer):
	os.makedirs(dirname)
	for (name, url) in attachments:
		print("Fetching %s" % name)
		r = s.get(fcc_url + url, headers=dict(Referer=referer))
		extension = r.headers['content-type'].split('/')[-1]
		filename = name + '.' + extension
		print("Writing %s" % filename)
		#print(lot[1] for lot in referer)
		####change folder name here

		with open(dirname + '/' + filename, 'wb') as handle:
			for chunk in r.iter_content():
				handle.write(chunk)

def load_next(fccid):
	appid, productid = parse_fccid(fccid)
	html_doc = lookup_fccid(appid, productid)
	#print(html_doc)
	productData = {}
	productData, more = parse_search_results(html_doc, productData)
	FromRec = 101
	while more:
		print("looping")
		html_doc = lookup_fccid(appid, productid, FromRec)
		productData, more = parse_search_results(html_doc, productData)
		FromRec += 100
	print("here")
	return productData
