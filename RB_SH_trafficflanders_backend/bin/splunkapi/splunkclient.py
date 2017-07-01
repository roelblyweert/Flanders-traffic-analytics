# $Id: splunkclient.py 2016-07-01 $
# Author: Roel Blyweert <blyweert.roel@gmail.com>
# Copyright: Roel Blyweert

import logging
import requests

class Splunkclient(object):
	def __init__(self, session_key, base_url='https://localhost:8089/', app_folder='BICS_App_pam' ):
		self.user_agent = 'splunk/traffic_flanders 1.00'
		self.session_key = session_key
		self.app_folder = app_folder
		self.base_url = base_url

	def create_headers(self):
		""" Creates the headers with the session key, if the session key is null
		:param session_key: the current users session key :return: a header
		dictionary """
		return {'user-agent': self.user_agent, 'Authorization':
			'Splunk %s' % self.session_key,
			 'Accept': 'application/json', 'Content-Type':
			 'application/json'}

	@staticmethod
	def extract_json(r):
	   """
	   :type r: Response :param r: :return: the json value, or throws errors
	   """
	   Splunkclient.handle_error(r)
	   return r.json()

	@staticmethod
	def handle_error(r):
		"""
		:type r: requests.Response :param r: :return: the response as given, or
		throws errors on, 4xx / 5xx """
		if r.status_code == 404:
			logger.error("Error from SplunkAPI %s with content: %s",
					   r.status_code, r.text)
			raise NotFoundError("Not Found", { 'url': r.url })	
		elif r.status_code >= 500:
			logger.error("Error from SplunkAPI %s with content: %s",
					   r.status_code, r.text)
		elif r.status_code >= 400:
			logger.error("Client Exception: " + json.dumps(r.json()) + "- HTTP status code: " + r.status_code)
		return r
