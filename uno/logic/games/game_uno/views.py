from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
#from util import Color, Player, Normal, Pull2, LoseTurn, Retour, ChangeColor, Pull4
from . import util

players = []
game = None

def index(request):
    return render(request, "index.html")

def add_user(request):
    if not "username" in request.GET:
        return JsonResponse({"success":False})
    
    username = request.GET['username']
    if username.strip() != "":
        players.append(util.Player(request.GET.get("username")))
        request.session['username'] = request.GET.get("username")
        return JsonResponse({"success":True})
    return JsonResponse({"success":False})
        

def start_game(request):
    global g
    g = util.Game()
    g.add_users(players)
    g.shuffle()
    return JsonResponse({"success":True})


def test(request):
    username = request.GET['username']
    print(username)
    return HttpResponse(username)

def get_status(request):
    if not "username" in request.GET:
        return JsonResponse({"success":False,"msg":"username does not exist"})
    if not "username" in request.session:
        return JsonResponse({"success":False,"msg":"no session"})

    username = request.GET['username']
    if request.session['username'] != username:
        return JsonResponse({"success":False, "msg": "You are not that user"})

    cards = g.users[username].cards
    users=[p.name for p in players]
    turn=g.next.name
    #ret = dict(
    #print(ret)
    print(request.session['id'])
    return JsonResponse(ret, safe=False)


def turn(request):
    pass
