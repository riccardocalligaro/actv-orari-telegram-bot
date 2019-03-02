import numpy as np
import pandas as pd
import datetime
feriale = True

def find_next_times(fermata):
    print(fermata)
    filename = 'stop_times.txt'
    filenametrips = 'trips.txt'
    filenameroutes = 'routes.txt'
    filenamestops = 'stops.txt'
    stop_requested = int(fermata)
    print(stop_requested)
    df = pd.read_csv(filename)
    dtrips = pd.read_csv(filenametrips)
    droutes = pd.read_csv(filenameroutes)
    dstops = pd.read_csv(filenamestops)


    stop_times = []
    tripsIds = []
    routes = []
    fermate = []
    names = []
    times = df[df.stop_id == int(fermata)]
    stop_times = times["arrival_time"].tolist()
    tripIds = times["trip_id"].values.tolist()
    tripStr = str(tripIds).replace(' ', '').replace('[', '').replace(']', '').split(',')
    for trip in tripStr:
        routes.append(dtrips.route_id[dtrips.trip_id == int(trip)])
    for route in routes:
        linea = droutes[droutes.route_id == int(route)]
        fermate.append((linea.route_short_name))
        names.append((linea.route_long_name))
    sorted_times = np.argsort(stop_times)
    tratte = sorted(stop_times)
    i = 0
    prevstop = " "
    results = []
    x = datetime.datetime.now()
    oraAttuale = x.strftime("%H")
    minutiAttuali = x.strftime("%M")
    for stop in tratte:
        if stop.strip() != prevstop.strip():
            parts = stop.split(':')
            if (parts[0] > oraAttuale) or (parts[0] == oraAttuale and parts[1] >= minutiAttuali):

                if parts[0][0] == '2' and int(parts[0][1])>=4:
                    s = list(stop)
                    s[0] = '0'
                    s[1] = str(int(s[1])-4)

                    results.append("🕒 Ora: {} 🚍 Codice: {} 📍Tratta: {}".format("".join(s), fermate[sorted_times[i]].to_string(index=False),names[sorted_times[i]].to_string(index=False) ))
                else:
                    results.append("🕒 Ora: {} 🚍 Codice: {} 📍Tratta: {}".format(stop, fermate[sorted_times[i]].to_string(index=False),names[sorted_times[i]].to_string(index=False) ))


        prevstop = stop
        i+=1

    results = results[:5]

    fermataAttuale = (dstops.stop_name[dstops.stop_id == int(fermata)]).to_string(index=False)
    output = "🕒 Ora corrente: {}:{}\n🚏 Fermata: {}\n\n".format(oraAttuale, minutiAttuali, fermataAttuale)
    #output = ""
    if not results:
        output+="😯 Nessun bus trovato per questa fermata."
        return output
    for result in results:
        output+= result+"\n\n"

    return output
