"""Parses webcomic pages to identify their navigation links and locate archived and new comics"""
import urllib
from StringIO import StringIO
from lxml import etree
from lxml import html

def findLinks(source, target):
	""" Returns a list of tuples with the xpath and content of every link from source URL
		to target URL"""
	links = []
	source_socket = urllib.urlopen(source)
	fixed_tree = etree.parse(source_socket, etree.HTMLParser())
	fixed_html = html.tostring(fixed_tree.getroot(), pretty_print=True, method="xml")
	absolute_document = html.document_fromstring(fixed_html, base_url=source)
	absolute_document.make_links_absolute()
	absolute_html = html.tostring(absolute_document, pretty_print=True, method="xml")
#	fixed_html = html.tostring(source_html.parse().getroot(),pretty_print=True, method="html")
#	print absolute_html
	context = etree.iterparse(StringIO(absolute_html), tag="a")
	for action, elem in context:
#		print(etree.tostring(elem))
		if "href" in elem.attrib:
			url = elem.attrib["href"]
			if url == target:
				links.append((etree.ElementTree(elem).getpath(elem), elem.text))
	source_socket.close()
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
