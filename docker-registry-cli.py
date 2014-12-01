#!/usr/bin/env python
#-*- coding:utf8 -*-
'''
A client tool request Docker Registry API to get information of images.
'''
# Author by: FengRen
# Email: zw.fengren@gmail.com
# Usage: python docker-registrycli.py http://docker_registry_ip:port

import sys
import urllib2
import json
from prettytable import PrettyTable


class Client(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.search_url = self.base_url + '/v1/search'
        self.tag_url = self.base_url + '/v1/repositories/'
        self.image_url = self.base_url + '/v1/images/'

    def get(self, url):
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            output = json.loads(response.read())
            return output
        except ValueError:
            print "Can't connect %s" % url
            sys.exit()

    def _get_tag(self, name):
        tag = self.get(self.tag_url + name + '/tags/latest')
        return tag

    def _get_image_info(self, image_id):
        image_info = self.get(self.image_url + image_id + '/json')
        return image_info

    def search(self):
        images = self.get(self.search_url)
        x = PrettyTable(["ID", "Name", "Cmd", "Entrypoint", 
                         "description", "Created"])
        x.align["name"] = 1
        for i in images.keys():
            if isinstance(images[i], list):
                for j in images[i]:
                    image_tag = self._get_tag(j["name"])
                    image_info = self._get_image_info(image_tag)
                    image_name = j["name"].split('/')[-1]
                    image_id = image_info['id'][:12]
                    image_description = j['description']
                    image_cmd = image_info['container_config']['Cmd'][0]
                    if isinstance(image_info['container_config']['Entrypoint'], list):
                        image_entrypoint = ' '.join(image_info['container_config']['Entrypoint'])
                    else:
                        image_entrypoint = image_info['container_config']['Entrypoint']
                    x.add_row([image_id, image_name,
                               image_cmd,
                               image_entrypoint,
                               image_description,
                               image_info['created']])
        return x

if __name__ == "__main__":
    try:
        docker_registry_url = sys.argv[1]
        client = Client(docker_registry_url)
        print client.search()
    except IndexError:
        print "Please enter a docker registry uri for search"
        print "Example:"
        print "\thttp://docker_registry:port/"
