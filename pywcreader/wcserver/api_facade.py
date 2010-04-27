"""Functions that implement each API HTTP method"""
import re
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import simplejson
from django.contrib.auth.models import User
from models import Comic, Episode

def listAllComics():
    """Lists all available comics"""
    return _comicsHttpResponse(Comic.objects.all());

def createUser(username, params):
    """Initializes a new user on the system"""
    if (not "password" in params) or (not params["password"]):
        return HttpResponse("Please supply a non-empty password", status=400)
    password = params["password"]
    if "email" in params:
        email = params["email"]
    else:
        email = ""
    User.objects.create_user(username, email, password)
    return _HttpResponseOk()

def updateUser(request):
    """Updates an user's data"""
    pass

def listFavoriteComics(user):
    """List a user's favorite comics"""
    return _comicsHttpResponse(user.get_profile().favorite_comics.all(), user)
    
def addFavorite(user, comic):
    """Adds a comic to a users' favorite list"""
    user.get_profile().favorite_comics.add(comic)
    return _HttpResponseOk()

def removeFavorite(user, comic):
    """Removes a comic from a users' favorite list"""
    user.get_profile().favorite_comics.remove(comic)
    return _HttpResponseOk()

def listReadEpisodes(user, comic):
    """Lists all episodes from a comic that the user has already read"""
    return _episodesHttpResponse(user.profile.read_episodes.filter(comic=comic).order_by("order"))  
        
def readEpisode(user, episode):
    """Marks an episode as 'read' by the user (and sets it as the last episode)"""
    user.get_profile().read(episode)
    return _HttpResponseOk()
    
def unreadEpisode(user, episode):
    """Marks an episode as 'not read' by the user (not touching the last read episode, however) """
    user.get_profile().unread(episode)
    return _HttpResponseOk()

def listEpisodes(comic):
    """Lists all episodes belonging to a code, in the proper order"""
    return _episodesHttpResponse(Episode.objects.filter(comic=comic).order_by("order"))    

def getEpisodeByUrl(url):
    """Retrieves the episode that matches an URL"""
    episodes = Episode.objects.filter(url=url)
    if episodes:
        return _episodeHttpResponse(episodes[0], next=True)
    else:
        return HttpResponseNotFound()
    
def getEpisode(episode):
    """Retrieves an episode's information (including next episode)"""
    return _episodeHttpResponse(episode, next=True)

def getComicByUrl(url):
    """Retrieves the comic that the URL is contained on.
    Should match the home, the episodes and pretty much any page on the comics' domain
    
    It's a bit naive (it chops the base domain from the rest and matches it against the
    home URL for performance reasons), but will work by now (and may be improved if and
    when comics show up not having a base domain)"""
    mo = re.match(r"^(.+?//.+?/)", url)
    comics = Comic.objects.filter(home_url=mo.group(1)) if mo else None
    if comics:
        return _comicHttpResponse(comics[0])
    else:
        return HttpResponseNotFound()

# Utility (non-api) methods
    
def _HttpResponseOk():
    return HttpResponse("Ok")    
    
def _episode_data(episode, next=False):
    """Returns a dictionary object with the episode's public data.
    If next=True AND we have a next episode, include its data (non-recusrively)"""
    episode_dict = {
        "title" : episode.title,
        "id" : "episode_%d" % episode.id,
        "url" : episode.url
        }
    if next:
        next_episode = episode.next()
        if next_episode:
            episode_dict["next_episode"] = _episode_data(next_episode, next=False)
    return episode_dict
    # todo adicionar comic_id acima, sem gerar queries
    
    
def _comic_data(comic, user=None):
    """Returns a dictionary object with the comic's public data
    If a user is passed, returns the private data (e.g., last read episode for the user)"""
    comic_dict = {
        "name" :  comic.name,
        "home_url" : comic.home_url,
        "id" : "comic_%d" % comic.id  
        }
    if user:
        lre = user.profile.last_read_episodes.filter(comic=comic)
        if lre:
            comic_dict["last_read_episode"] = _episode_data(lre[0], next=True)
    return comic_dict

def _comicHttpResponse(comic, user=None):
    """Returns a response with JSON-formatted data for a single comic (with optional user-related data)"""
    return HttpResponse(simplejson.dumps(_comic_data(comic, user)))

def _comicsHttpResponse(comics, user=None):
    """Returns a response with JSON-formatted data for a list of comics (with optional user-related data)"""
    return HttpResponse(simplejson.dumps([_comic_data(comic, user)
          for comic in comics]))    

def _episodeHttpResponse(episode, next=False):
    """Returns a response with JSON-formatted data for a single episode"""
    return HttpResponse(simplejson.dumps(_episode_data(episode, next)))

def _episodesHttpResponse(episodes):
    """Returns a response with JSON-formatted data for a list of episodes"""
    return HttpResponse(simplejson.dumps([_episode_data(episode)
          for episode in episodes]))    
