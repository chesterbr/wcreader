"""WebComic Reader API views"""
from django.http import Http404, HttpResponse, HttpResponseNotFound, QueryDict
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson, datastructures
from django.contrib.auth.models import User
import re
from pywcreader.wcserver import api_facade
from wcserver.models import Comic, Episode

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
    
    # Dispath
    if re.match(r"^/comics/?$", path) and request.method == "GET":
        return api_facade.listAllComics();
    if re.match(r"^/user_"+username+"/$", path) and request.method == "PUT":
        return user_exists(user) or api_facade.createUser(username, params)
    if re.match(r"^/user_"+username+"/comic_[0-9]+?/read_episodes/$", path) and request.method == "GET":
        return user_missing(user) or comic_missing(comic) or api_facade.listReadEpisodes(user, comic)
    if re.match(r"^/user_.+?/episode_[0-9]+?/$", path) and request.method == "PUT":
        return user_missing(user) or episode_missing(episode) or api_facade.readEpisode(user, episode)
    if re.match(r"^/user_.+?/episode_[0-9]+?/$", path) and request.method == "DELETE":
        return user_missing(user) or episode_missing(episode) or api_facade.unreadEpisode(user, episode)
    if re.match(r"^/comic_[0-9]+?/episodes/$", path) and request.method == "GET":
        return comic_missing(comic) or api_facade.listEpisodes(comic)
    
#    if re.match(r"^/user_.+?/$", path) and request.method == "POST":
#        return user_missing(user) or api_facade.updateUser(user, params)
#    if re.match(r"^/user_.+?/comics/$", path) and request.method == "GET":
#        return user_missing(user) or api_facade.listFavoriteComics(user)

    return HttpResponse("Bad Request (check API docs)", status=400)

# Helper methods for condition checking on the dispatcher

def user_missing(user):
    """ If the user is missing, returns an error """
    return HttpResponse("Username not found", status=400) if not user else None 

def comic_missing(comic):
    """ If the user is missing, returns an error """
    return HttpResponse("Comic not found", status=400) if not comic else None 

def episode_missing(episode):
    """ If the episode is missing, returns an error """
    return HttpResponse("Episode not found", status=400) if not episode else None 

def user_exists(user):
    """ If the user exists, returns an error """
    return HttpResponse("Username already on the database, use POST to modify", status=400) if user else None
