#!/usr/bin/env python3

from pyFCC.archive import get_attachment_urls, parse_fccid, load_next, fetch_and_pack
import sys

if __name__ == '__main__':
	# if len(sys.argv) in (2, 3):
	# 	(appid, productid) = parse_fccid(*sys.argv[1:])
	if len(sys.argv) <2:
		print("Usage: archive.py <FCC id>")
		sys.exit(1)
	for fccid in sys.argv[1:]:
		print("Looking up FCC id: %s" % fccid)
		###############call to function here
		productData = load_next(fccid)
		#appid, productid = parse_fccid(fccid)
		#html_doc = lookup_fccid(appid, productid)
		#productData = parse_search_results(html_doc)

		for key, value in productData.items():
			for x, row in enumerate(value, 1):
				detail_url, ID, low, high = row
				print("Fetching result %d" % x)
				appid, productid = parse_fccid(ID)
				print(appid, productid)

				attachments = get_attachment_urls(detail_url)
				dirname = "%s/%s/%d" % (appid, productid, x)
				fetch_and_pack(attachments, dirname, detail_url)
