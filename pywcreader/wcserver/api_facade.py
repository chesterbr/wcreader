import re
from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.auth.models import User
from wcserver.models import Comic, Episode

def http_ok():
    return HttpResponse("Ok")

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
    return http_ok()

def updateUser(request):
    """Updates an user's data"""
    pass

def listReadEpisodes(user, comic):
    """Lists all episodes from a comic that the user has already read"""
    return HttpResponse(simplejson.dumps([{
            "title" : episode.title,
            "id" : "episode_%d" % episode.id,
            "url" : episode.url
         } for episode in user.profile.read_episodes.filter(comic=comic).order_by("order")]))    

#def listFavoriteComics(user):
#    pass

#def lastEpisode(request):
#    """Retrieves the last episode read from a comic for the current user.
#    last = user.last_read_episodes.filter(comic=comic)
#    if last:
#        return simplelast[0]
#    else:
#        return
#    """    
        
def readEpisode(user, episode):
    """Marks an episode as 'read' by the user (and sets it as the last episode)"""
    user.get_profile().read(episode)
    return http_ok()
    
def unreadEpisode(user, episode):
    """Marks an episode as 'not read' by the user (not touching the last read episode, however) """
    user.get_profile().unread(episode)
    return http_ok()

def listEpisodes(comic):
    """Lists all episodes belonging to a code, in the proper order"""
    return HttpResponse(simplejson.dumps([{
            "title" : episode.title,
            "id" : "episode_%d" % episode.id,
            "url" : episode.url
         } for episode in Episode.objects.filter(comic=comic).order_by("order")]))    
    