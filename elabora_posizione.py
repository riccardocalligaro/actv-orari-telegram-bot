from scipy import spatial
import pandas as pd

def elabora_coordinate(lat, lon):
    filename = './files/stops.txt'
    df = pd.read_csv(filename)
    stops_lat = df['stop_lat'].values.tolist()
    stops_lon = df['stop_lon'].values.tolist()
    results = []
    for i in range(0, len(stops_lat)):
        results.append((stops_lat[i],stops_lon[i]))

    tree = spatial.KDTree(results)
    result = tree.query([(lat, lon)])
    indice = result[1]
    indice = int(str(indice).replace(']','').replace('[', ''))

    fermata = df[(df.stop_lat == results[indice][0]) & (df.stop_lon == results[indice][1])]
    try:
        ris = int((fermata.stop_id).to_string(index=False).strip())
    except Exception as e:
        return "Errore nella conversione .elabora_posizone.py"

    return ris
    #return "🚏 Fermata: " + (fermata.stop_name).to_string(index=False).strip() + "\n🆔 Codice: " + (fermata.stop_id).to_string(index=False).strip()
