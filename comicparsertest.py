import unittest
import comicparser

class FindLinks(unittest.TestCase):
	def testSingleLink(self):
		"""findLinks should be able to correctly identify a single "next" link between a source and a target page"""
		links = comicparser.findLinks("testfiles/testcomic/1.html", "testfiles/testcomic/2.html")
		self.assertEqual(len(links), 1) # we just have the "next" link from episode 1 to episode 2
		self.assertEqual(links[0][1], "Next")
		
	def testMultipleLink(self):
		"""findLinks should return a multi-item list if there is more than one link between the pages"""
		links = comicparser.findLinks("testfiles/testcomic/2.html", "testfiles/testcomic/1.html")
		self.assertEqual(len(links), 2) # there are a "previous" and a "first" link from 2 to 1
		self.assertEqual(links[0][1], "First")
		self.assertEqual(links[1][1], "Previous")
	
	def testNoLink(self):
		"""findLinks should return an empty list if no links are found from source to target"""
		links = comicparser.findLinks("testfiles/testcomic/1.html", "testfiles/testcomic/3.html")
		self.assertFalse(links) # no links from episode 1 to episode 3
		
class Navigate(unittest.TestCase):
	def setUp(self):
		(self.xpath, self.expected_html) =  \
			comicparser.findLinks("testfiles/testcomic/2.html", "testfiles/testcomic/3.html")[0]

	def testNextOnLast(self):
		"""getNext should not return a link if we are on the last one"""
		self.assertFalse( \
			comicparser.getNext("testfiles/testcomic/4.html", self.xpath, self.expected_html))
	
	def testNextOnFirst(self):
		"""getNext should also not work on the first page (because the links are shifted)"""
		self.assertFalse( \
			comicparser.getNext("testfiles/testcomic/1.html", self.xpath, self.expected_html))
	
	def testNextInSecond(self):
		"""getNext should return a link to the third page"""
		next = comicparser.getNext("testfiles/testcomic/2.html", self.xpath, self.expected_html)
		self.assertTrue(next)
		self.assertEqual(next, "testfiles/testcomic/3.html")

if __name__ == "__main__":
    unittest.main()   