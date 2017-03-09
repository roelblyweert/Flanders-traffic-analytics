# $Id: verkeer_config_proc.py 2016-03-09 $
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

##################
# SUBROUTINES PART ###########
##################

# function that processes the XML configuration data and store this in a dictionary
def processConfigData(xmldata):
	# initialize resulting variable
	resulting_data = []
	# read the XML content
	root = etree.fromstring(xmldata)
	
	# parse the data via a loop
	for meetpunt_entry in root:
		if meetpunt_entry.tag == "meetpunt": # only process in case 
			# create dictionary containing some identifiers
			entry_data = meetpunt_entry.attrib

			# go through all data in the entry
			for data in meetpunt_entry:
				entry_data[data.tag] = data.text

			# append to the resulting list
			resulting_data.append(entry_data)

	# return list containing the configuration data
	return resulting_data

# function that clears the configuration KV store collection and pushes the new configuration data
def pushToKvStore(data, splunkhost, splunkuser, splunkpw, splunkapp, splunkcollection):
	print "pushing to KV store.."
	
	
##################
# MAIN ###########
##################
	
#OUTPUT OPTIONS
_DEBUG = 1
FILENAME = os.path.splitext(os.path.basename(__file__))[0]

# Read the configuration file
config = ConfigParser.SafeConfigParser()
file_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'default')
conf = os.path.join(file_dir, "verkeerdata.conf")
config.read(conf)
splunkhost = config.get('splunk', 'host')
splunkuser = config.get('splunk', 'user')
splunkpw = config.get('splunk', 'password')
splunkapp = config.get('splunk', 'app')
splunkcollection = config.get('splunk', 'collection')

# retrieve data
xmldata = urllib2.urlopen("http://miv.opendata.belfla.be/miv/configuratie/xml").read()
config_data = processConfigData(xmldata) # process dataset
pushToKvStore(config_data, splunkhost, splunkuser, splunkpw, splunkapp, splunkcollection) # write result to KV store
