from django.db import models
import parser
from django.contrib.auth.models import User

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
    home_url = models.CharField(max_length=2000, null=False, db_index=True);
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
        if self.strategy == "N":
            last_episode = self.episode_set.order_by("-order")[0]
            next_comic_url = parser.getNext(
                last_episode.url,
                self.next_button_xpath,
                self.next_button_expected_html,
            )
            if next_comic_url:
                e = Episode()
                e.comic = self
                e.order = last_episode.order + 1
                e.url = next_comic_url
                if self.episode_title_xpath:
                    e.title = parser.getTextForXpath(next_comic_url, self.episode_title_xpath)
                else:
                    # TODO
                    pass
                e.save()
                return True            
        return False

class Episode(models.Model):
    """Each webcomic is divided in episodes, which are required to have unique URLs"""
    comic = models.ForeignKey(Comic)
    order = models.IntegerField()
    title = models.CharField(max_length=500)
    url = models.CharField(max_length=2000, db_index=True)
    
    def __unicode__(self):
        return self.comic.name + " - " + self.title
    
    def next(self):
        """Returns the "next" episode, if available"""
        episodes = Episode.objects.filter(comic=self.comic).filter(order=self.order + 1)
        return episodes[0] if episodes else None
    
class UserProfile(models.Model):
    """Users are stored on Django's facility. This class extends it to allow linking them to comics, episodes and such"""
    user = models.ForeignKey(User, unique=True)    
    read_episodes = models.ManyToManyField(Episode, related_name="read_by_users")
    last_read_episodes = models.ManyToManyField(Episode, related_name="last_read_by_users")
    favorite_comics = models.ManyToManyField(Comic)
    
    def read(self, episode):
        """Marks an episode as "read" (also making it the last-read-episode) """
        self.read_episodes.add(episode)
        last_read = self.last_read_episodes.filter(comic=episode.comic)
        if last_read:
            self.last_read_episodes.remove(last_read[0])
        self.last_read_episodes.add(episode)
        
    def unread(self, episode):
        """Removes the "read" status from an episode (without affecting the last-read)"""
        self.read_episodes.remove(episode)
        
        
def initNextBasedComic(name, home_url, url_episode_1, url_episode_2, url_episode_3, title_episode_2="", episode_title_xpath=""):
    """Creates a new next-harvesting-based webcomic on the database.
    
    It needs the comic name, URL for the first three episodes and title for the third
    (to deduce the title xpath)
    
    It can search for the title xpath by receving the second episode's title, or receive
    the xpath directly. If no xpath is supplied or searched, episodes will have
    auto-generated titles. 
    
    Returns the newly created comic"""
    
    # Comic setup (finding the next button and, if needed, title xpath)
    c = Comic()
    c.name = name
    c.home_url = home_url
    c.strategy = "N"
    links = parser.findLinks(url_episode_2, url_episode_3)
    if links:
        (c.next_button_xpath, c.next_button_expected_html) = links[0]
    else:
        raise ValueError("Can't find link from " + url_episode_2 + " to " + url_episode_3)
    if not episode_title_xpath:
        if title_episode_2:
            episode_title_xpath = parser.findXpathFor(url_episode_2, title_episode_2)
            if not episode_title_xpath:
                raise ValueError("Can't find element containing title '" + title_episode_2 + "' at " + url_episode_2)
    
    # Initial episodes setup
    (e1, e2) = (Episode(), Episode())
    (e1.order, e2.order) = (1, 2)
    (e1.url, e2.url) = (url_episode_1, url_episode_2)
    if episode_title_xpath:
        c.episode_title_xpath = episode_title_xpath
        (e1.title, e2.title) = (parser.getTextForXpath(url_episode_1, episode_title_xpath),
                                parser.getTextForXpath(url_episode_2, episode_title_xpath))
    
    # Persist the comic, then the episodes
    # (the object association is lost if you do it before saving)
    c.save()
    (e1.comic, e2.comic) = (c, c)
    e1.save()
    e2.save()

    return c
    
"""Cool trick: auto-create user profiles when they are accessed.
   from: http://www.djangorocks.com/hints-and-tips/automatically-create-a-django-profile.html"""    
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
    
