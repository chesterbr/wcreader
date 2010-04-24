"""WebComic Reader API views"""
from django.http import Http404, HttpResponse, HttpResponseNotFound, QueryDict
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson, datastructures
from models import Comic, Episode, User
import re

def dispatch(request):
    """Translates the request into one of the operations defined below"""
    if re.match(r"/comics/?", request.path) and request.method == "GET":
        return listAllComics(request);
    if re.match(r"/user_.+?/", request.path):
        if request.method == "PUT":
            return createUser(request)
        elif request.method == "POST":
            return updateUser(request)
    if re.match(r"/user_.+/comic_.+/read_episodes", request.path) and request.method == "GET":
        return listReadEpisodes(request)
    return HttpResponse("<h1>Bad Request</h1>", status=400)

def listAllComics(request):
    """Lists all available comics"""
    
    comics = Comic.objects.all();
    return HttpResponse(simplejson.dumps([{
            "name" :  comic.name,
            "home_url" : comic.home_url,
            "id" : "comic_%d" % comic.id                               
        } for comic in comics]))


def createUser(request):
    """Initializes a new user on the system"""
    username = getUsername(request)
    if not re.match("^[a-zA-Z0-9_]{1,15}$", username):
        return HttpResponse("Invalid username (wanted alphanmeric 1-15 chars, got " + username + ")", status=400)
    if User.objects.filter(username=username):
        return HttpResponse("Username already on the database, use POST to modify", status=400)
    PUT = QueryDict(request.raw_post_data, encoding=request.encoding)    
    if (not "password" in PUT) or (not PUT["password"]):
        return HttpResponse("Please supply a non-empty password", status=400)
    password = PUT["password"]
    if "email" in PUT:
        email = PUT["email"]
    else:
        email = ""
    User.objects.create_user(username, email, password)
    return HttpResponse("<h1>Ok</h1>")

def updateUser(request):
    """Updates an user's data"""
    pass

def listReadEpisodes(request):
    try:
        comic = Comic.objects.filter(id=getComic_id(request))[0]
        user = User.objects.filter(username=getUsername(request))[0]
    except ObjectDoesNotExist:
        return HttpResponse("Comic or user not found", status=404)
    
    return HttpResponse(simplejson.dumps([{
            "title" : episode.title,
            "url" : episode.url
         } for episode in user.profile.read_episodes.filter(comic=comic)]))
    

def lastEpisode(request):
    """Retrieves the last episode read from a comic for the current user.
    
    Comic is identified by its ID"""
    try:
        comic = Comic.objects.get(id=request.REQUEST["id"])
        user = User.objects.get(username=request.REQUEST["username"])
    except ObjectDoesNotExist:
        raise Http404 # melhorar isso
    
    last = user.last_read_episodes.filter(comic=comic)
    if last:
        return last[0]
        
        
def readEpisode(request):
    """Marks an episode as 'read' by the user (by means of its URL)"""
    
    try:
        episode = Episode.objects.get(url=request.REQUEST["url"])
        user = User.objects.get(username=request.REQUEST["username"])
    except ObjectDoesNotExist:
        raise Http404 # melhorar isso

    user.read(episode)
    
    

def getUsername(request):
    """Returns the username from the current request, or None if none found"""
    mo = re.search(r"/user_(.+?)/", request.path)
    if mo:
        return mo.group(1)
    else:
        return None
        
def getComic_id(request):
    """Returns the comic ID from the current request, or None if none found"""
    mo = re.search(r"/comic_(.+?)/", request.path)
    if mo:
        return mo.group(1)
    else:
        return None
        