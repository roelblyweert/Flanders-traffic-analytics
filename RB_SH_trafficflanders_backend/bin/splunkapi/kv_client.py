# $Id: kv_client.py 2016-07-01 $
# Author: Roel Blyweert <blyweert.roel@gmail.com>
# Copyright: Roel Blyweert

import json
import requests
from splunkapi.splunkclient import Splunkclient

class KVClient(Splunkclient):
    def __init__(self, session_key, base_url='https://localhost:8089/', app_folder='RB_SH_trafficflanders_backend'):
        """

        :rtype: splunkapi.KVClient
        """
        super(KVClient, self).__init__(session_key, base_url, app_folder)

    def get_document(self, kvstore, document_id, username):
        """

        :param kvstore:
        :param document_id:
        :param username:
        :rtype: dict
        :return:
        """
        username = 'nobody'
        return self.extract_json(requests.get(
            self.base_url + 'servicesNS/' + username + '/' + self.app_folder +'/storage/collections/data/' + kvstore + '/' + document_id
            + '?output_mode=json',
            headers=self.create_headers(),
            verify=False))

    def get_documents(self, kvstore, username, limit='50', skip='0'):
        """

        :param kvstore: the store to use
        :param username: the user to fetch docs for
        :param limit: Maximum number of items to return. For example, to return five items, use limit=5.
        :param skip: Number of items to skip from the start. For example, to skip the first ten items, use skip=10.
        :rtype dict
        :return: documents
        """
        username = 'nobody'
        return self.extract_json(requests.get(
            self.base_url + 'servicesNS/' + username + '/'+ self.app_folder +'/storage/collections/data/' + kvstore +
            '?output_mode=json&limit='+limit+'&skip='+skip,
            headers=self.create_headers(),
            verify=False))

    def create_document(self, kvstore, username, data):
        """

        :param kvstore:
        :param username:
        :param data:
        :return: the key of the document
        """
        username = 'nobody'
        r = requests.post(
            self.base_url + 'servicesNS/' + username + '/' + self.app_folder + '/storage/collections/data/' + kvstore + '?output_mode=json',
            data=json.dumps(data),
            headers=self.create_headers(),
            verify=False)
        return self.extract_json(r).get('_key')

    def update_document(self, kvstore, document_id, username, data):
        """
        Beware an update of a document is always a full update, not a partial update. Always submit full document.
        :param kvstore:
        :param document_id:
        :param username:
        :type dict
        :param data:
        :return: the key of the updated document
        """
        username = 'nobody'
        return self.extract_json(requests.post(
            self.base_url + 'servicesNS/' + username + '/' + self.app_folder + '/storage/collections/data/' + kvstore
            + '/' + document_id + '?output_mode=json',
            data=json.dumps(data),
            headers=self.create_headers(),
            verify=False)).get('_key', '')

    def update_documents(self, kvstore, user, docs):
        """
        Batch update / create documents
        :param kvstore: 
        :param user: 
        :param docs: 
        :return: list of keys that have been created 
        :rtype: list
        """
        username = 'nobody'
        return self.extract_json(requests.post(
            self.base_url + 'servicesNS/' + username + '/' + self.app_folder + '/storage/collections/data/' + kvstore
            + '/batch_save?output_mode=json',
            data=json.dumps(docs),
            headers=self.create_headers(),
            verify=False))

    def delete_document(self, kvstore, username, document_id):
        """
        Delete an entry from the given kvstore by it's key.
        :param kvstore: 
        :param username: 
        :param document_id: 
        :return: True if deleted, throws NotFound if it does not exist
        """
        username = 'nobody'
        return self.handle_error(requests.delete(
            self.base_url + 'servicesNS/' + username + '/' + self.app_folder + '/storage/collections/data/' + kvstore
            + '/' + document_id + '?output_mode=json',
            headers=self.create_headers(),
            verify=False)).status_code == 200

    def delete_documents(self, kvstore, username, query):
        username = 'nobody'
        json_query_query = self.base_url + 'servicesNS/' + username + '/' + self.app_folder + '/storage/collections/data/' + kvstore + '/?output_mode=json&query=' + query
        return self.handle_error(requests.delete(json_query_query,
                                                 headers=self.create_headers(),
                                                 verify=False)).status_code == 200
