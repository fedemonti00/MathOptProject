import re
from datetime import datetime, timedelta

# Mappa squadra → ID
team_ids = {
    "Argentino": 1, "Atenas": 2, "Bahía Basket": 3, "Bahia Basket": 3,
    "Boca Jrs": 4, "Ciclista Olímpico": 5, "Olimpico LB": 5,
    "Estudiantes C.": 6, "Ferrocarril O.": 7, "GECR Indalo": 8,
    "Instituto C.": 9, "Sionista": 10, "Lanus": 11, "Lanús": 11,
    "Libertad S.": 12, "Obras Basket": 13, "Penarol": 14, "Peñarol": 14,
    "Quilmes MP": 15, "Quimsa": 16, "Regatas C.": 17, "San Lorenzo": 18,
    "San Martin C.": 19, "La Union": 20
}

# Genera mappa date → numero
date_to_index = {}
start_date = datetime.strptime("Sep 23, 2015", "%b %d, %Y")
end_date = datetime.strptime("Nov 28, 2015", "%b %d, %Y")
current = start_date
index = 1
while current <= end_date:
    date_str = current.strftime('%b %d, %Y')  # senza punto
    date_to_index[date_str] = index
    current += timedelta(days=1)
    index += 1

# Regex per date come "Sep. 23, 2015" o "Sep 23, 2015"
date_regex = re.compile(r'\b([A-Z][a-z]{2})\.?\s+(\d{1,2}),\s+2015\b')

# Funzione per convertire una riga
def convert_schedule(text):
    lines = text.strip().split('\n')
    results = []
    for line in lines:
        # Rimuove punteggio
        line = re.sub(r'\t\d+-\d+(\sOT)?', '', line)

        # Sostituisce squadre con ID
        match = re.search(r'([A-Za-zÁÉÍÓÚÑñüÜ.\s]+?)\s*-\s*([A-Za-zÁÉÍÓÚÑñüÜ.\s]+)', line)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            id1 = team_ids.get(team1)
            id2 = team_ids.get(team2)
            if id1 and id2:
                line = re.sub(re.escape(match.group(0)), f" {id1}-{id2}", line)
            else:
                print(f"[!] Squadra non trovata: {team1}, {team2}")

        # Sostituisce date con numeri
        def replace_date(m):
            month, day = m.groups()
            try:
                date_obj = datetime.strptime(f"{month} {int(day)}, 2015", "%b %d, %Y")
                date_str = date_obj.strftime("%b %d, %Y")
                return str(date_to_index.get(date_str, date_str))
            except ValueError:
                return m.group(0)

        line = date_regex.sub(replace_date, line)
        results.append(line)
    return "\n".join(results)

# File I/O
input_file = "data/games.txt"
output_file = "data/games_id.txt"

with open(input_file, "r", encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
    for line in fin:
        new_line = convert_schedule(line)
        fout.write(new_line + "\n")
