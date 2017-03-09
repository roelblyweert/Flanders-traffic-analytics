# $Id: verkeer_data_proc.py 2016-03-09 $
# Author: Roel Blyweert <blyweert.roel@gmail.com>
# Copyright: Roel Blyweert

"""
This script that gets traffic data from all regions in Flanders
"""

import sys, datetime, json, os , os.path as op, time, urllib2
import ConfigParser
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
		if meetpunt_entry.tag == "meetpunt": # only process in case 
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
						dict_data["klasse_" + klasse_id][meetdata.tag] = meetdata.text
				elif data.tag == "rekendata":
					# go through all reken data
					for rekendata in data:
						dict_data[rekendata.tag] = rekendata.text
				else:
					dict_data[data.tag] = data.text

			print json.dumps(dict_data)
	
##################
# MAIN ###########
##################
	
#OUTPUT OPTIONS
_DEBUG = 1
FILENAME = os.path.splitext(os.path.basename(__file__))[0]

# retrieve data
xmldata = urllib2.urlopen("http://miv.opendata.belfla.be/miv/verkeersdata").read()
processData(xmldata) # process dataset
