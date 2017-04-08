# $Id: verkeer_config_proc.py 2016-04-08 $
# Author: Roel Blyweert <blyweert.roel@gmail.com>
# Copyright: Roel Blyweert

"""
This script that gets traffic configuration data from all regions in Flanders
"""

import sys, datetime, json, os , os.path as op, time, urllib2
import ConfigParser
import json
import urllib2
import urllib
import re

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
			print entry_data

			# go through all data in the entry
			for data in meetpunt_entry:
				##########################################################################
				## following lines are needed due to data quality and data encoding issues
				# read the text and cast to a string object
				txt = str(data.text)
				# replace commas by periods in the context of proper numerical handling
				txt = txt.encode('utf-8')
				txt = re.sub("\xe2\x80\x93", "-", txt) # remove en dash
				txt = txt.encode('ascii')
				txt = txt.replace(",", ".")
				##########################################################################
				
				# check the format of the data
				if (txt.isdigit() or txt.replace('.','',1).isdigit()):
					#print txt + " - float"
					entry_data[data.tag] = float(txt)
				else: 
					#print txt + " - string"
					entry_data[data.tag] = txt

			# append to the resulting list
			resulting_data.append(entry_data)

	# return list containing the configuration data
	return resulting_data

# function that clears the configuration KV store collection and pushes the new configuration data
def pushToKvStore(data, splunkapp, splunkcollection, session_key):
	print "pushing to KV store.."

# login into Splunk
def loginSplunk(host, username, password):
	print "Login into Splunk.."
	
	# login into Splunk and get a session key
	base_url = "https://" + host + ":8089"
	request = urllib2.Request(base_url + '/servicesNS/%s/search/auth/login' % (username), 
	data = urllib.urlencode({'username': username, 'password': password}))
	server_content = urllib2.urlopen(request)
	session_key = minidom.parseString(server_content.read()).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
	common_logging.log_debug("sessionKey=" + session_key)
	
	# return the session key so it can be used later on
	return session_key
	
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
print config_data

#session_key = loginSplunk(splunkhost, splunkuser, splunkpw)
#pushToKvStore(config_data, splunkapp, splunkcollection, session_key) # write result to KV store
