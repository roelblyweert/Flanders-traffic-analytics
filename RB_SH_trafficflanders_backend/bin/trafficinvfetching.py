# $Id: traffic_inv_fetching.py 2018-01-05 $
# Author: Roel Blyweert <blyweert.roel@gmail.com>
# Copyright: Roel Blyweert
# coding=utf-8

import sys, datetime, json, time, urllib2
import ConfigParser
import json
import urllib2
import urllib
import re
import os, os.path as op
import logging
import logging.handlers

# Import ElementTree package for walking over XML trees
import elementtree.ElementTree as etree

# import the Splunk modules
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators

# custom search command definition
@Configuration()
class TrafficInvFetchingCommand(GeneratingCommand):
	
	# main function containing the functionality belonging to the generating command
	def generate(self):
		# define the URL
		fetch_url = "http://miv.opendata.belfla.be/miv/configuratie/xml"
		
		# fetch, process and push the data to the KV store
		xmldata = self.fetchData(fetch_url) # fetch 
		processed_xml = self.processConfigData(xmldata) # process
		#self.writeDataToOutput(processed_xml) # push to the output of the custom search command
		
		for entry in processed_xml:
			yield entry

	# function to fetch the XML sensor inventory data
	def fetchData(self, url):
	 	xmldata = urllib2.urlopen(url).read()
	 	return xmldata
	 		
	# function that processes the XML configuration data and store this in a dictionary
	def processConfigData(self, xmldata):
	 	# initialize resulting variable
	 	resulting_data = []
	 	# read the XML content
	 	root = etree.fromstring(xmldata)
	 	
	 	# parse the data via a loop
	 	for meetpunt_entry in root:
	 		if meetpunt_entry.tag == "meetpunt": # only process in case of a meetpunt XML tag
	 			# create dictionary containing some identifiers
	 			entry_data = meetpunt_entry.attrib
	 
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

# run the command specified in the class above
dispatch(TrafficInvFetchingCommand, sys.argv, sys.stdin, sys.stdout, __name__)
