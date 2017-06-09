#!/usr/bin/env python3

from pyFCC.archive import parse_fccid, lookup_fccid, parse_search_results, get_attachment_urls, fetch_and_pack
from pyFCC.fccDB import create_product_table, populate_products
import sys

if __name__ == '__main__':
	# if len(sys.argv) in (2, 3):
	# 	(appid, productid) = parse_fccid(*sys.argv[1:])
	if len(sys.argv) <2:
		print("Usage: archive.py <FCC id>")
		sys.exit(1)
	for fccid in sys.argv[1:]:
		print("Looking up FCC id: %s" % fccid)
		appid, productid = parse_fccid(fccid)
		html_doc = lookup_fccid(appid, productid)
		productData = parse_search_results(html_doc)

		for key, value in productData.items():
			for x, row in enumerate(value, 1):
				detail_url, ID, low, high = row
				print("Fetching result %d" % x)
				appid, productid = parse_fccid(ID)
				print(appid, productid)

				attachments = get_attachment_urls(detail_url)
				dirname = "%s/%s/%d" % (appid, productid, x)
				fetch_and_pack(attachments, dirname, detail_url)
	
	create_product_table()
	populate_products(productData)