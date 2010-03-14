# coding=UTF-8

from django.db import models
from django.db.models import Max
import parser


class Comic(models.Model):
	"""A webcomic (e.g.: "xkcd", "Questionable Content").
	
	Each webcomic has a strategy for retrieving its data:
	
	- Next Button Harvesting: The system will search for a "Next" link on the comic's last
		page, checking if there is a new comic pointed there
	- Archive Listing: The system will monitor an "archives" page, trying to find the next
		comic there
	- URL Pattern: The system will look for numbered URLs, e.g., it would see
		"http://mycomic.com/view.php?id=1234" and try to find the next one as 1235.
	"""
	
	STRATEGY_CHOICES = (
		("N", "Next Button Harvesting"),
		("L", "Archive Listing"),
		("U", "URL pattern")
	)
	name = models.CharField(max_length=255)
	strategy = models.CharField(max_length=1, choices=STRATEGY_CHOICES)
	next_button_xpath = models.CharField(max_length=500, null=True)
	next_button_expected_html = models.CharField(max_length=2000, null=True)
	episode_title_xpath = models.CharField(max_length=500, null=True)
	archive_url = models.CharField(max_length=2000, null=True)
	url_pattern = models.CharField(max_length=2000, null=True)
	
	def __unicode__(self):
		return self.name
		
	def update(self):
		"""Checks if a comic has a new episode, and, if so, update the comic"""
		if self.strategy=="N":
			last_episode_order = self.episode_set.aggregate(Max('order'))["order__max"]
			last_episode_url = self.episode_set.filter(order__exact=last_episode_order)[0].url
			next_comic_data = parser.getNext(
				last_episode_url,
				self.next_button_xpath,
				self.next_button_expected_html,
				self.episode_title_xpath
			)
			if next_comic_data:
				e = Episode()
				e.comic = self
				e.order = last_episode_order + 1
				e.url = next_comic_data[0]
				e.title = next_comic_data[1]
				e.save()

class Episode(models.Model):
	"""Each webcomic is divided in episodes, which are required to have unique URLs"""
	comic = models.ForeignKey(Comic)
	order = models.IntegerField()
	title = models.CharField(max_length=500)
	url = models.CharField(max_length=2000)
	
	def __unicode__(self):
		return self.comic.name + " - " + self.title
	
class User(models.Model):
	openid = models.CharField(max_length=2000)
	
# Representar no user uma coleção de comics, onde cada um terá:
# - status: favorito, inativo, that kind of stuff
# - ponteiro para o último episode lido
# Opcional, decidir: - coleção dos episódios já lidos (é legal pra poder fazer um checklist, mas
# torna a escalabilidade mais complicada)