# $Id: traffic_inv_kvstore.py 2016-07-02 $
# Author: Roel Blyweert <blyweert.roel@gmail.com>
# Copyright: Roel Blyweert

import sys, datetime, json, time, urllib2
import ConfigParser
import json
import urllib2
import urllib
import re
import os, os.path as op
import logging
import logging.handlers

# Import of add-on specific modules
from splunkapi.splunkclient import Splunkclient
from splunkapi.kv_client import KVClient

# Import ElementTree package for walking over XML trees
import elementtree.ElementTree as etree

# import the Splunk modular inputs related modules
from splunklib.modularinput import *
import splunk

class TrafficInvToKVStore(Script):
	"""
	Main class for the modular input inheriting from the Script class.
	The Script class is an abstract class shipped with the Splun SDK and used for modular inputs specifically.
	"""
	
	# constructor of TrafficInvToKVStore
	def __init__(self):
		# call the constructor of its parent class
		super(TrafficInvToKVStore, self).__init__()
		# initialize the logging system
		self.logger = self.setup_logging()
	
	# subroutine to get the scheme from the modular input
	def get_scheme(self):
		# Returns scheme.
		scheme = Scheme("Flanders Traffic inventory to KV store modular input")
		scheme.description = "Captures inventory information from the traffic related sensors in Flanders via its open data platform and pushes this to the KV store."
		
		# add the fetch URL as an argument
		endpoint_argument = Argument("fetch_url")
		endpoint_argument.title = "Remote inventory fetching URL"
		endpoint_argument.data_type = Argument.data_type_string
		endpoint_argument.description = "This URL is the source of the XML data containing the sensor inventory data information for all measuring points."
		endpoint_argument.require_on_create = True
		scheme.add_argument(endpoint_argument)
		
		# add the destination KV store collection as an argument
		hostname_argument = Argument("dest_collection")
		hostname_argument.title = "Destination KV store collection"
		hostname_argument.data_type = Argument.data_type_string
		hostname_argument.description = "This is the destination KV store collection name where the sensor inventory data will be stored."
		hostname_argument.require_on_create = True
		scheme.add_argument(hostname_argument)
		
		return scheme
	
	# subroutine to validate the inputs of the modular input
	def validate_input(self, validation_definition):
		self.logger.info("validate_inputs: " + time.strftime("%d-%m-%Y %H:%M:%S"))
		
		# get the parameters
		fetch_url = validation_definition.parameters["fetch_url"]
		dest_collection = validation_definition.parameters["dest_collection"]
		
		self.logger.info("fetch_url" + fetch_url)
		self.logger.info("dest_collection" + dest_collection)
		
	def stream_events(self, inputs, ew):
		# Splunk Enterprise calls the modular input, streams XML describing the inputs to stdin,
		# and waits for XML on stdout describing events. The stdout is the data that gets indexes in Splunk.
		# The stin also includes a session_key that can be used to communicate with the Splunk REST API.
		
		# some debugging logs
		self.logger.debug("stream_events: " + time.strftime("%d-%m-%Y %H:%M:%S"))
		self.logger.debug("metadata: " + str(inputs.metadata))
		self.logger.debug("session_key: " + inputs.metadata['session_key'])
		session_key = inputs.metadata['session_key'] # read the session key
		
		# loop through the actual modular inputs settings
		for input_name, input_item in inputs.inputs.iteritems():
			# read the URL and the destination KV store collection
			fetch_url = input_item['fetch_url']
			dest_collection = input_item['dest_collection']
			
			# some debugging output
			self.logger.debug("fetch_url " + fetch_url)
			self.logger.debug("dest_collection " + dest_collection)
						  
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
		
		print os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME)
		splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
		splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
		logger.addHandler(splunk_log_handler)
		splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
		
		# some logging in case of successful initialization.
		logger.info("Script started and logging initialized correctly.")
		
		return logger

# main entry point of the modular input
if __name__ == "__main__":
    sys.exit(TrafficInvToKVStore().run(sys.argv))
