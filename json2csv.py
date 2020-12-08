#!/usr/bin/env python
# usage: 
# python json2csv "jsonfile" "csvfile"


import json
import csv
import sys

def main():
	js_file = sys.argv[1]
	csv_file = sys.argv[2]
	with open(js_file, 'r') as f:
		data = json.load(f)	

	with open(csv_file, 'w+') as f:
		f_csv = csv.writer(f)
		f_csv.writerow(data[0].keys())
		for row in data:
			f_csv.writerow(row.values())
	

if __name__ == '__main__':
	main()
