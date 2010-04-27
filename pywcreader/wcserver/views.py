"""WebComic Reader API views"""
from django.http import Http404, HttpResponse, HttpResponseNotFound, QueryDict
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson, datastructures
from django.contrib.auth.models import User
import re
from pywcreader.wcserver import api_facade
from models import Comic, Episode
import time
import base64

def dispatch(request):
    """Translates the request into one of the operations defined below"""

    # Get the components from URL (with related objects), and body parameters 
    path = request.path + ("/" if request.path[-1] != "/" else "")
    mo_user = re.search(r"/user_(.+?)/", path)
    mo_comic = re.search(r"/comic_(.+?)/", path)
    mo_episode = re.search(r"/episode_(.+?)/", path)
    user = comic = episode = None
    username = ""
    if mo_user:
        username = mo_user.group(1)
        if not re.match("^[a-zA-Z0-9_]{1,15}$", username):
            return HttpResponse("Invalid username (wanted alphanmeric 1-15 chars, got " + username + ")", status=400)
        users = User.objects.filter(username=username)
        if users:
            user = users[0]
    if mo_comic:
        comics = Comic.objects.filter(id=mo_comic.group(1))
        if comics:
            comic = comics[0]
    if mo_episode:
        episodes = Episode.objects.filter(id=mo_episode.group(1))
        if episodes:
            episode = episodes[0]
    params = QueryDict(request.raw_post_data, encoding=request.encoding)
    url = request.GET["url"] if "url" in request.GET else None
        
    # Dispatch
    if re.match(r"^/comics/?$", path) and request.method == "GET":
        return api_facade.listAllComics();
    if re.match(r"^/episode/?$", path) and request.method == "GET":
        return no_url(url) or api_facade.getEpisodeByUrl(url)
    if re.match(r"^/comic/?$", path) and request.method == "GET":
        return no_url(url) or api_facade.getComicByUrl(url)
    if re.match(r"^/comic_[0-9]+?/episodes/$", path) and request.method == "GET":
        return comic_missing(comic) or api_facade.listEpisodes(comic)
    if re.match(r"^/user_" + username + "/$", path) and request.method == "PUT":
        return user_exists(user) or api_facade.createUser(username, params)
    if re.match(r"^/user_" + username + "/comic_[0-9]+?/read_episodes/$", path) and request.method == "GET":
        return user_invalid(user, username, request) or comic_missing(comic) or api_facade.listReadEpisodes(user, comic)
    if re.match(r"^/user_" + username + "/episode_[0-9]+?/$", path) and request.method == "PUT":
        return user_invalid(user, username, request) or episode_missing(episode) or api_facade.readEpisode(user, episode)
    if re.match(r"^/user" + username + "/episode_[0-9]+?/$", path) and request.method == "DELETE":
        return user_invalid(user, username, request) or episode_missing(episode) or api_facade.unreadEpisode(user, episode)
    
#    if re.match(r"^/user_.+?/$", path) and request.method == "POST":
#        return user_missing(user) or api_facade.updateUser(user, params)
#    if re.match(r"^/user_.+?/comics/$", path) and request.method == "GET":
#        return user_missing(user) or api_facade.listFavoriteComics(user)

    return HttpResponse("Bad Request (check API docs)", status=400)

# Helper methods for validating parameters and conditions
# They either return an error response, or none, allowing chained returns like:
#     return cond1() or cond2() or cond3() or desired_result()

def user_invalid(user, username, request):
    """ Returns an appropriate response if the username does not exist or is not authenticated """
    # Code heavily inspired on this snippet: http://www.djangosnippets.org/snippets/243/ by Scanner
    # Credentials must exist, refer to the queried user and be valid
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                if (uname == username) and user.check_password(passwd):
                    return None
    # If no valid credentials were found, ask the user-agent for valid ones                
    response = HttpResponse("Please supply valid credentials for " + username, status=401)
    response['WWW-Authenticate'] = 'Basic realm="wcreader"'
    return response

def no_url(url):
    """ If there is no url GET parameter, returns an error """
    return HttpResponse("Please supply an URL", status=400) if not url else None     

def comic_missing(comic):
    """ If the comic is missing, returns an error """
    return HttpResponse("Comic not found", status=400) if not comic else None 

def episode_missing(episode):
    """ If the episode is missing, returns an error """
    return HttpResponse("Episode not found", status=400) if not episode else None 

def user_exists(user):
    """ If the user exists, returns an error """
    return HttpResponse("Username already on the database, use POST to modify", status=400) if user else None
