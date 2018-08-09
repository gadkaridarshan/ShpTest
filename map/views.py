from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse

import json
import geocoder
import requests
import os
import datetime

from urllib.parse import urlencode
from urllib3 import request as Request
import requests
import base64

import sys

from oauth2client.client import OAuth2WebServerFlow


# Importing Models
from map.models import Coordinate

ACCESS_TOKEN = ''

# ========================================================================
# Main view
# @param {request} : Django Request
# @return Rendered view from index.html
# ========================================================================
def index(request):
    return TemplateResponse(request, 'index.html', {})

# ========================================================================
# Method that'll refresh access token, thanks to refresh token
# @param {CLIENT_ID} : Google Public Client Identifier
# @param {CLIENT_SECRET} : Google Secret Client Identifier
# @param {REFRESH_TOKEN} : Refresh Token provided using Google Callback
# @return response['access_token'] : String access token (3600s)
# ========================================================================
def refreshAccessToken(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN):
    TOKEN_REFRESH_URI = "https://www.googleapis.com/oauth2/v3/token"
    data={
    'grant_type':    'refresh_token',
    'client_id':     CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'refresh_token': REFRESH_TOKEN
    }
    headers={
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = json.loads(requests.post(TOKEN_REFRESH_URI,data=data,headers=headers).text)
    return response['access_token']

# ========================================================================
# Method that'll generate an unique identifier for coordinates
# @param {ADDRESS} : Address passed in parameter
# @param {LAT} : Latitude from Coordinate
# @param {LNG} : Longitude from Coordinate
# ========================================================================
def id_generator(ADDRESS,LAT,LNG):
    import hashlib, binascii
    prehash = ADDRESS + "_" + str(LAT) + "_" + str(LNG)
    dk = hashlib.pbkdf2_hmac('sha256', str.encode(prehash), b'salt', 100000)
    return binascii.hexlify(dk)

# ========================================================================
# Method that'll display URI address to get the access and refresh tokens
# @param {request} : Django Request
# ========================================================================
def initRefreshToken(request):

    CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    REDIRECT_URI = os.environ.get('REDIRECT_OAUTH2')
    SCOPE = os.environ.get('SCOPE_FUSION_TABLES')

    flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                           client_secret=CLIENT_SECRET,
                           scope=SCOPE,
                           redirect_uri="http://localhost:8000")

    return HttpResponse("Init Refresh Token")

# ========================================================================
# Method that'll check the validity of a given access token
# Displays a report based on OAuth data (time remaining, client...)
# @param {request} : Django Request
# @param {access_token} : Access Token to be checked
# ========================================================================
def checkToken(request, access_token):

    url_check_token = "https://www.googleapis.com/oauth2/v2/tokeninfo"
    param_check = {'access_token': access_token}
    r = requests.post(url_check_token, params=param_check)
    return HttpResponse("Check Token")

# ========================================================================
# Returns all coordinates stored in Fusion Tables
# @param {request} : Django Request
# @return {JsonResponse(r.json())} : JSON Array with the list of coord.
# ========================================================================
def getAllCoordinates(request):
    global ACCESS_TOKEN
    table_id   = os.environ.get('GOOGLE_FUSION_TABLE_ID')
    CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')
    ACCESS_TOKEN = refreshAccessToken(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
    # Headers and parameters for API Call
    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN ,'Content-Type': 'application/json', 'Host': 'www.googleapis.com'}
    params = {'sql':"SELECT * FROM " + table_id}
    r = requests.post("https://www.googleapis.com/fusiontables/v2/query", params=params, headers=headers)
    return JsonResponse(r.json())

# ========================================================================
# Clear all addresses (Fusion tables and Django Database)
# @param {request} : Django Request
# @return {HttpResponse("Clear Addresses Tables")}
# ========================================================================
def clearAddresses(request):

    table_id   = os.environ.get('GOOGLE_FUSION_TABLE_ID')
    SCOPE = os.environ.get('SCOPE_FUSION_TABLES')
    url_api    = 'https://www.googleapis.com/fusiontables/v2/query'
    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN ,'Content-Type': 'application/json', 'Host': 'www.googleapis.com'}
    params = {'sql':"DELETE FROM " + table_id}
    r = requests.post("https://www.googleapis.com/fusiontables/v2/query", params=params, headers=headers)
    # Clear all coordinates in Database
    Coordinate.objects.all().delete()

    return HttpResponse("Clear Addresses Tables")

# ========================================================================
# Will receive the request callback with the authorization code
# Will display the token (refresh and access)
# @param {request} : Django Request
# @return {HttpResponse("Clear Addresses Tables")}
# ========================================================================
def oauth(request):
    # Get the code from URI callback on this endpoint ( ?code='XXXXXXXXX...')
    OAUTH_CODE = request.GET['code']

    if OAUTH_CODE != None:
        CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
        CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
        REDIRECT_URI = os.environ.get('REDIRECT_OAUTH2')

        # Your application requests an access token and refresh token from Google
        data = urlencode({
          'code': OAUTH_CODE,
          'client_id': CLIENT_ID,
          'client_secret': CLIENT_SECRET,
          'redirect_uri': REDIRECT_URI,
          'grant_type': 'authorization_code'
        })

        request = Request(
          url='https://www.googleapis.com/oauth2/v4/token',
          data=data)
        request_open = requests.get(request)

        # Google returns access token, refresh token, and expiration of
        # access token
        response = request_open.read()
        request_open.close()
        tokens = json.loads(response)

        # print(tokens)

    return HttpResponse(OAUTH_CODE)

# ========================================================================
# Will be called to transmit coordinates from Google Maps on
# Front-end (events)
# @param {request} : Django Request
# @param {action} : can be used later for extra features (eg delete coord.)
# @param {value} : Encoded coordinates from Client
# @return {HttpResponse("sendCoordinate called")}
# ========================================================================
def sendCoordinate(request,action=None,value=None):
    global ACCESS_TOKEN
    # Special characters encoded on client
    value    = value.replace("FLAGEQUAL",'=')
    value    = value.replace("FLAGPLUS",'+')
    value    = value.replace("FLAGSLASH",'/')
    value += "=" * ((4 - len(value) % 4) % 4)
    value    = base64.b64decode(value)
    json_obj = json.loads(value)
    lat = json_obj['lat']
    lng = json_obj['lng']
    # Reverse geocoder, will get data on coordinate based on lat/lng
    g = geocoder.google([lat, lng], method='reverse')
    tmpCoordinate = g.json
    # Coordinate validation (if user clicked on a "real" address)
    if(tmpCoordinate['ok'] == True):
        # Environement variables
        TABLE_ID   = os.environ.get('GOOGLE_FUSION_TABLE_ID')
        CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
        CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
        REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')
        # Data from tmpCoordinate (reverse Geocoding)
        address   = tmpCoordinate['address']
        lat       = tmpCoordinate['lat']
        lng       = tmpCoordinate['lng']
        unique_id = id_generator(address,lat,lng).decode('latin1')
        creation  = datetime.datetime.now().isoformat()
        # If the address is fine, we'll check if it already exists before inserting it in the DBMS and Fusion tables
        # See access_token_from_refresh
        # Parameters for request (headers, params)
        headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN ,'Content-Type': 'application/json', 'Host': 'www.googleapis.com'}
        params = {'sql':"SELECT COUNT() FROM " + TABLE_ID + " WHERE Unique_ID = '" + unique_id + "'"}
        r = requests.post("https://www.googleapis.com/fusiontables/v2/query", params=params, headers=headers)
        # If rows is not in objects keys, there's no identical coordinate
        if not 'rows' in r.json().keys():
            query2 = "INSERT INTO " +  TABLE_ID + " (Unique_ID, Address, Latitude, Longitude, Creation) VALUES ('"+unique_id+"', '"+address+"', '"+str(lat)+"', '"+str(lng)+"', '"+creation+"')"
            params2 = {'sql': query2}
            r2 = requests.post("https://www.googleapis.com/fusiontables/v2/query", params=params2, headers=headers)
            # Insertion in Database
            p = Coordinate(Unique_ID=unique_id, Latitude=lat, Longitude=lng, Address=address, Creation=creation)
            p.save()
        else:
           print("Address already exists")
    return HttpResponse("sendCoordinate called")
