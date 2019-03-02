import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import datetime
global ids

def trova_tratta(route_selected):
    global ids
    global shortnames
    filename = './files/routes.txt'
    df = pd.read_csv(filename)
    route = df[df.route_short_name == route_selected.upper()]
    ids = []
    shortnames = []
    longnames =[]
    for row in route.itertuples():
        ids.append(getattr(row, "route_id"))
        shortnames.append(getattr(row, "route_short_name"))
        longnames.append(getattr(row, "route_long_name"))
    output = ""
    for i in range(0, len(ids)):
        output += "📍 {} 🚏 {} - {} \n\n".format(str(i+1),shortnames[i],longnames[i])
    return output

def trova_trips(tratta_scelta):
    global feriale
    global tripsFeriali
    global tripsFestive
    global ids
    global nome_tratta
    global tripSpeciale

    try:
        tratta_scelta = int(tratta_scelta)
    except Exception as e:
        return "⛔️ Non posso convertre lettere in numeri!"

    id = ids[int(tratta_scelta)-1]
    nome_tratta = int(tratta_scelta)-1


    filename = './files/trips.txt'
    file2 = './files/calendar_dates.txt'

    df = pd.read_csv(filename)
    dt = pd.read_csv(file2)

    # controlla giorno della settimana
    giornataOggi = datetime.date.today().strftime("%Y%m%d")
    if datetime.datetime.today().weekday() is 6:
        feriale = False
    else:
        feriale = True

    tripsFeriali = []
    tripsFestive = []
    exepDates = []
    trips = df[df.route_id == int(id)]
    service_execptions = dt.service_id.to_string(index=False)
    parts = service_execptions.split('\n')
    if not dt[dt.date == giornataOggi].empty:
        feriale = False
    if not de[de.service_id == giornataOggi].empty:
        feriale = False
    # la giornata é festiva quando il service id finsice con 18 / 03 / 09
    for row in trips.itertuples():
        if (getattr(row, "service_id")[-6:][:2])== '03' or (getattr(row, "service_id")[-6:][:2])== '09' or (getattr(row, "service_id")[-6:][:2])== '18':
            tripsFestive.append(getattr(row, "trip_id"))
        else:
            tripsFeriali.append(getattr(row, "trip_id"))

def trova_fermate(stop):
    global closestMatches
    filename = './files/stops.txt'
    df = pd.read_csv(filename)
    fermate = []
    output = ""
    if (df.stop_id[df.stop_name == stop]).empty:
        for row in df.itertuples():
            fermate.append(getattr(row, "stop_name"))
        closestMatches = process.extract(stop, fermate, limit=15)
        i = 1
        for match, corrispondenza in closestMatches:
            output += "📍:" + str(i) + " "+ match + " corrispondenza: " + str(corrispondenza) + "%" + "\n"
            i+=1
        return output
    else:
        stop_requested = df.stop_id[df.stop_name == stop].to_string(index=False)

    if len(stop_requested.split('\n')) > 1:
        stop_requested = stop_requested.split('\n')[0].replace(' ','')
    return trova_tabella_orari(stop_requested)

def trova_fermata_corrispondenza(scelta):
    global closestMatches
    filename = './files/stops.txt'
    df = pd.read_csv(filename)
    stop_requested = df.stop_id[df.stop_name == closestMatches[int(scelta)-1][0]].to_string(index=False)
    if len(stop_requested.split('\n')) > 1:
        stop_requested = stop_requested.split('\n')[0].replace(' ','')
    return trova_tabella_orari(stop_requested)

def trova_tabella_orari(stop_requested):
    global feriale
    global nome_tratta
    global tripsFeriali
    global tripsFestive
    global tripSpeciale
    filename = './files/stop_times.txt'
    pd.set_option('display.max_colwidth',1000)
    df = pd.read_csv(filename)
    fermate = []

    if feriale:
        for trip in tripsFeriali:
            trips = df[df.trip_id == int(trip)]
            for row in trips.itertuples():
                if int(getattr(row, "stop_id")) == int(stop_requested):
                    fermate.append(getattr(row, "departure_time"))
    else:
        for trip in tripsFestive:
            trips = df[df.trip_id == int(trip)]
            for row in trips.itertuples():
                if int(getattr(row, "stop_id")) == int(stop_requested):
                    fermate.append(getattr(row, "arrival_time"))
    if feriale:
        giornata = "feriale"
    else:
        giornata = "festiva"
    fermateSorted = sorted(set(fermate))
    if not fermateSorted:
        return "😶 Non é stata trovata alcuna corrispondenza"
    output = "🚌 Linea {}\n🚏Fermata: {}\n🌅Giornata: {} \n\n".format(shortnames[nome_tratta],stop_requested, giornata)
    for fermata in fermateSorted:
        output+= "🕒 "+ fermata + "\n"

    return output
