# $Id: verkeer_data_proc.py 2016-04-08 $
# Author: Roel Blyweert <blyweert.roel@gmail.com>
# Copyright: Roel Blyweert

"""
This script that gets traffic data from all regions in Flanders
"""

import sys, datetime, json, os , os.path as op, time, urllib2
import json
import urllib2

# Import ElementTree package for walking over XML trees
import elementtree.ElementTree as etree

# function that processes the XML data and outputs in JSON format
def processData(xmldata):
	#print "Processing XML data.."
	# read the XML content
	root = etree.fromstring(xmldata)
	
	# parse the data via a loop
	for meetpunt_entry in root:
		if meetpunt_entry.tag == "meetpunt": # only process in case of a meetpunt tag
			# create dictionary containing some identifiers
			dict_data = meetpunt_entry.attrib

			# go through all data in the entry
			for data in meetpunt_entry:
				# only go further with processing for the meetdata and rekendata tags
				if data.tag == "meetdata":
					klasse_id = data.attrib["klasse_id"]
					dict_data["klasse_" + klasse_id] = {}

					# go through all meet data
					for meetdata in data:
						if is_number(meetdata.text):
							dict_data["klasse_" + klasse_id][meetdata.tag] = int(meetdata.text)
						else:
							dict_data["klasse_" + klasse_id][meetdata.tag] = meetdata.text
				elif data.tag == "rekendata":
					# go through all reken data
					for rekendata in data:
						if is_number(rekendata.text):
							dict_data[rekendata.tag] = int(rekendata.text)
						else:
							dict_data[rekendata.tag] = rekendata.text
				else:
					if is_number(data.text):
						dict_data[data.tag] = int(data.text)
					else:
						dict_data[data.tag] = data.text

			print json.dumps(dict_data)

def is_number(s):
	try:
		int(s)
		return True
	except ValueError:
		pass
				 
	return False

	
##################
# MAIN ###########
##################
	
#OUTPUT OPTIONS
_DEBUG = 1
FILENAME = os.path.splitext(os.path.basename(__file__))[0]

# retrieve data
xmldata = urllib2.urlopen("http://miv.opendata.belfla.be/miv/verkeersdata").read()
processData(xmldata) # process dataset
