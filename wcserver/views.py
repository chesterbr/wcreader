"""WebComic Reader API views"""
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from models import Comic, Episode, User

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
    
    
        
