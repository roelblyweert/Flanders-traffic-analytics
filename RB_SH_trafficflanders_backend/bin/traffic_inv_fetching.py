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
import splunk
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators

# custom search command definition
@Configuration()
class TrafficInvFetchingCommand(GeneratingCommand):
	
	# constructor of TrafficInvFetchingCommand
	def __init__(self):
		# call the constructor of its parent class
		super(TrafficInvFetchingCommand, self).__init__()
		# initialize the logging system
		self.logger = self.setup_logging()
	
	# main function containing the functionality belonging to the generating command
	def generate(self):
		# define the URL
		fetch_url = "http://miv.opendata.belfla.be/miv/configuratie/xml"
		
		# some debugging output
		self.logger.debug("fetch_url " + fetch_url)
		
		# fetch, process and push the data to the KV store
		xmldata = self.fetchData(fetch_url) # fetch 
		processed_xml = self.processConfigData(xmldata) # process
		self.writeDataToOutput(processed_xml) # push to the output of the custom search command

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
			
	# function that writes the results to the output of the custom search command
	def writeDataToOutput(self, config_data):
		# loop through the results of coming from the open data platform and write them to the KV store
		for document in config_data:
			yield document
						  
	# logging setup subroutine
	def setup_logging(self):
		"""
		Setup logging
		Log is written to /opt/splunk/var/log/splunk/traffic_inv_kvstore.log
		"""
		FILENAME = os.path.splitext(os.path.basename(__file__))[0]
		logger = logging.getLogger('splunk.' + FILENAME)
		logger.setLevel(logging.INFO)
		SPLUNK_HOME = os.environ['SPLUNK_HOME']
		
		LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
		LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
		LOGGING_STANZA_NAME = 'python'
		LOGGING_FILE_NAME = FILENAME + ".log"
		BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
		LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
		
		splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
		splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
		logger.addHandler(splunk_log_handler)
		splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
		
		# some logging in case of successful initialization.
		logger.info("Script started and logging initialized correctly.")
		
		return logger


# run the command specified in the class above
dispatch(TrafficInvFetchingCommand, sys.argv, sys.stdin, sys.stdout, __name__)
