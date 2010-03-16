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
        
    def checkNewEpisode(self):
        """Checks if a comic has a new episode, and, if so, update the comic"""
        if self.strategy=="N":
            last_episode = self.episode_set.order_by("-order")[0]
            next_comic_data = parser.getNext(
                last_episode.url,
                self.next_button_xpath,
                self.next_button_expected_html,
                self.episode_title_xpath
            )
            if next_comic_data:
                e = Episode()
                e.comic = self
                e.order = last_episode.order + 1
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
    username = models.CharField(max_length=32)
    read_episodes = models.ManyToManyField(Episode, related_name="read_by_users")
    last_read_episodes = models.ManyToManyField(Episode, related_name="last_read_by_users")
    favorite_comics = models.ManyToManyField(Comic)
    
    def read(self, episode):
    	"""Marks an episode as "read" """
    	self.read_episodes.add(episode)
    	last_read = self.last_read_episodes.filter(comic=episode.comic)
    	if last_read:
    		self.last_read_episodes.remove(last_read[0])
    	self.last_read_episodes.add(episode)
    
