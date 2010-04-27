"""Functions that implement each API HTTP method"""
import re
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import simplejson
from django.contrib.auth.models import User
from models import Comic, Episode

def listAllComics():
    """Lists all available comics"""
    comics = Comic.objects.all();
    return HttpResponse(simplejson.dumps([{
            "name" :  comic.name,
            "home_url" : comic.home_url,
            "id" : "comic_%d" % comic.id                               
        } for comic in comics]))

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
    episodes = Episode.objects.filter(url=url)
    if episodes:
        return _episodeHttpResponse(episodes[0])
    else:
        return HttpResponseNotFound()

def getComicByUrl(url):
    """Returns the comic for which that URL belongs to (using the home URL as a URL base)"""
    pass

# Utility (non-api) methods
    
def _HttpResponseOk():
    return HttpResponse("Ok")    
    
def _episode_data(episode):
    """Returns a dictionary object with the episode's public data"""
    return {
        "title" : episode.title,
        "id" : "episode_%d" % episode.id,
        "url" : episode.url
        }

def _episodesHttpResponse(episodes):
    """Returns a response with JSON-formatted data for a list of episodes"""
    return HttpResponse(simplejson.dumps([_episode_data(episode)
          for episode in episodes]))    

def _episodeHttpResponse(episode):
    """Returns a response with JSON-formatted data for a single episode"""
    return HttpResponse(simplejson.dumps(_episode_data(episode)))    
