#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import traceback
import urllib2,urllib

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    
    try:
       req = request.get_json(silent=True, force=True)

       print("Request:")
       print(json.dumps(req, indent=4))
    
       res = processRequest(req)

       res = json.dumps(res, indent=4)
       # print(res)
       r = make_response(res)
       r.headers['Content-Type'] = 'application/json'
       return r
    #ludo !!!
    except  Exception as e:
        print(str(e))
        var = traceback.format_exc()
        print(str(var))

#a changer pour appelrer google (done!! )
def processRequest(req):
    if req.get("result").get("action") == "yahooWeatherForecast":
        return doYahooForecast(req)
    elif req.get("result").get("action") == "googleGeocoder":
        return doGoogleGeocoder(req)
    else:
         return {}
        
#fonction pour recuperer selment l'adresse de la phrase     
def get_neccesaire(query):
    phrase=query
    ici=phrase.find("adresse")     #chercher le mor cle "adresse" (ici recoit position du mot adresse)
    ici= ici+10                     #eplacer le cursus +8 pour passer au mot suivant 
    icii=phrase[ici:]              #prendre toute la chaine de caractere qui suit le mot adresse (ca doit etre l'adresse)
    print("le necessaire est ")    #trest pour voir si ca marche  
    print(icii)                    #test si ca marche 
    return (icii)

#case chercher une adresse fonction [doGoogleGeocoder]
def doGoogleGeocoder(req):
    print("doGoogleGeocoder")            #test a supprimer apres
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    result = req.get("result")
    parameters = result.get("resolvedQuery")
    print("j'ai eu ca de l'api.ai")
    print(parameters)                    #good
    #city = parameters.get("location")   #get le lieu de l'API.AI et le stocker dans "city"
    #if city is None:                    #si le lieu n'existe pas , ne retourne rien 
     #   return None
                                         #sinon on affiche l'adresse du lieu.
                                         #la fonction locu_serch recoit comme param le lieu qu'on cherche son adresse
    
   
    city = get_neccesaire(parameters)    #la variable "city" recoir la chaine de caractere de l'adresse from ["get_neccesaire"]
    print("voila l'adresse a chercher:") #test a supprimer apres
    print(city)                          #test a supprimer apres
    addresse = locu_serch(city)          #la variable adresse recoit le vrais adresse (exp: 14 rue paul dautier, 78140, France)
    return {
        "speech": addresse,
    }


#python 2.7 pour chercher l'adresse d'un local
def locu_serch(query): 
                                            #la variable addresss recoit la ville a chercher
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    address=query
    final_url = url + "&address=" + address #url + le mot "address=" + "la ville" a chercher
    response = urllib2.urlopen(final_url)
    data =  json.loads(response.read())     #"la fonction google marche tres bien" 
    add = "adresse : "   
    x=0
    for item in data["results"][0]["address_components"]:
        add = add + "\n" + data["results"][0]["address_components"][x]["long_name"]
        x=x+1
    return addresse #add
    
    

def doYahooForecast(req):
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}
    
    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))
    
    speech = "aujourd'hui a " + location.get('city') + ", la temperature est " + condition.get('temp') + " F"

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
