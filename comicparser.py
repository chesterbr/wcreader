"""Parses webcomic pages to identify their navigation links and locate archived and new comics"""
import urllib
from StringIO import StringIO
from lxml import etree
from lxml import html

def findLinks(source, target):
	""" Locates all links from the source URL to the target URL, returning a list 
		of 2-element tuples with each link's xpath and inner HTML """
	links = []
	source_socket = urllib.urlopen(source)
	absolute_tree = html.document_fromstring(source_socket.read(), base_url=source)
	absolute_tree.make_links_absolute()
	source_socket.close()
	context = etree.iterwalk(absolute_tree, tag="a")
	for action, elem in context:
		if "href" in elem.attrib:
			url = elem.attrib["href"]
			if url == target:
				links.append((etree.ElementTree(elem).getpath(elem), elem.text))
	return links

def getNext(source, xpath, expected_html):
	""" If the link in the xpath contains a link with the expected html and an href that does
		point somewhere else (i.e., not "#"), returns its href 
		(which should be the next comic, if that source is a non-last webcomic episode)"""
	next = None
	source_socket = urllib.urlopen(source)
	source_html = html.document_fromstring(source_socket.read(), base_url=source)
	source_html.make_links_absolute()
	links = source_html.xpath(xpath)
	if len(links) == 1:
		link = links[0]
		if link.text == expected_html:
			""" TODO: checar se nao e # """
			next = link.attrib["href"]
	source_socket.close()
	return next
	
def removePrefix(url):
	return url.rpartition("/")[2];
