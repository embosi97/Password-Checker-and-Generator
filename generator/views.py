from django.shortcuts import render
from random import randrange
from django.http import HttpResponse
import string
import random
import requests
import hashlib
from hitcount.models import HitCount

# Create your views here.


def home(request):
    return render(request, 'generator/home.html')


def password(request):

    pw = ''

    chars = ''

    spechar = '!@#$%^&+_-*'

    length = int(request.GET.get('length', 10))

    if(str(request.GET.get('case')) == "lowercase"):
        chars = string.ascii_lowercase
        characters = list(chars)

    elif (str(request.GET.get('case')) == "uppercase"):
        chars = string.ascii_uppercase
        characters = list(chars)

    elif (str(request.GET.get('case')) == "both"):
        chars = string.ascii_lowercase
        characters = list(chars)
        characters.extend(string.ascii_uppercase)

    if (request.GET.get('specialchar') and (str(request.GET.get('specialoption')) == "scattered")):
        characters.extend(spechar)

    if (request.GET.get('numbers') and (str(request.GET.get('numberoption')) == "scattered")):
        characters.extend(map(str, range(0, 10, 1)))

    for x in range(length):
        pw += random.choice(characters)

    if ((str(request.GET.get('numberoption')) == "back") and (str(request.GET.get('specialoption')) == "scattered")):
        pw = list(pw)
        pw[len(pw) - 1] = random.randrange(10)
        pw[len(pw) - 2] = random.randrange(10)
        pw = ''.join(map(str, pw))

    elif ((str(request.GET.get('numberoption')) == "scattered") and (str(request.GET.get('specialoption')) == "back")):
        spechar = list(map(str, spechar))
        pw = list(pw)
        pw[len(pw) - 1] = random.choice(spechar)
        pw[len(pw) - 2] = random.choice(spechar)
        pw = ''.join(map(str, pw))

    elif ((str(request.GET.get('numberoption')) == "back") and (str(request.GET.get('specialoption')) == "back")):
        spechar = list(map(str, spechar))
        pw = list(pw)

        if(random.randrange(10) > 5):
            pw[len(pw) - 1] = random.randrange(10)
            pw[len(pw) - 2] = random.choice(spechar)
            pw = ''.join(map(str, pw))
        else:
            pw[len(pw) - 1] = random.choice(spechar)
            pw[len(pw) - 2] = random.randrange(10)
            pw = ''.join(map(str, pw))

    return render(request, 'generator/password.html', {'password': pw})


def request_api_data(apassword):
    url = 'https://api.pwnedpasswords.com/range/' + apassword
    res = requests.get(url)
    if res.status_code != 200:
        raise RuntimeError(
            f'Error fetching: {res.status_code}, check the api and try again')
    return res


def get_password_leaks_count(hashes, tail):
    hashes = (line.split(':') for line in hashes.text.splitlines())
    for h, count in hashes:
        if h == tail:
            return count
    return 0


def pwned_api_check(bpassword):
    sha1password = hashlib.sha1(bpassword.encode('utf-8')).hexdigest().upper()
    first5_char, tail = sha1password[:5], sha1password[5:]
    response = request_api_data(first5_char)
    return get_password_leaks_count(response, tail)


def final_passwordcount(request):
    pw = str(request.GET.get('checked'))
    pwcount = pwned_api_check(pw)
    return render(request, 'generator/checked.html', {'checkedpassword': pwcount})
