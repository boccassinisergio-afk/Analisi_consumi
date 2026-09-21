from matplotlib import pyplot as plt
import pandas as pd
from google.cloud import bigquery

client = bigquery.Client()

# attendo il risultato con .result() per evitare che lo script avanzi prima che dataset e tabelle siano stati creati

with open('queries/00_create_tables.sql', 'r') as file:
    contenuto = file.read()
    create_tables = client.query(contenuto)
    result = create_tables.result()

# il file contiene due SELECT separate da ';': le splitto ed eseguo separatamente, assegnando ciascun risultato a un DataFrame

with open('queries/01_analisi_consumi_e_prezzi.sql', 'r') as file:
    contenuto = file.read().split(';')
    queries_ripulite = [stringa.strip() for stringa in contenuto if stringa.strip()]

df_picco = client.query(queries_ripulite[0]).result().to_dataframe()
df_fascia = client.query(queries_ripulite[1]).result().to_dataframe()

# totale kWh e importo per ogni combinazione utente+fascia

df_bolletta = df_picco.groupby(['id_utente', 'nome', 'fascia']).agg({'kwh_consumati': 'sum', 'importo': 'sum'}).reset_index()
df_pulito = df_picco[['id_utente', 'kwh_picco']].drop_duplicates(subset=['id_utente'])

df_temp = df_bolletta.merge(df_pulito, on='id_utente')

# rinomino le colonne con nomi ambigui, per evitare conflitti prima del merge successivo

df_fascia.rename(columns={'fascia': 'fascia_piu_costosa', 'importo': 'importo_fascia_piu_costosa', 'consumo': 'kwh_fascia_piu_costosa'}, inplace=True)

df_definitivo = df_temp.merge(df_fascia, on='id_utente')

# costruzione del report testuale, un blocco per utente

stringhe_da_formattare = []

for id, gruppo in df_definitivo.groupby('id_utente'):
    stringa_singola = f"Utente {gruppo['nome'].iloc[0]}\n"

    for indice, riga in gruppo.iterrows():
        stringa_singola += f"Fascia {riga['fascia']}: {riga['kwh_consumati']:.2f} → €{riga['importo']:.2f}\n\n"

    # kwh_picco e fascia_piu_costosa sono ripetuti identici su ogni riga dello stesso utente, quindi basta il primo valore
    stringa_singola += f"Picco di consumo: {gruppo['kwh_picco'].iloc[0]:.2f} kwh\nFascia più costosa: {gruppo['fascia_piu_costosa'].iloc[0]} → €{gruppo['importo_fascia_piu_costosa'].iloc[0]:.2f}"

    stringhe_da_formattare.append(stringa_singola)

print('\n\n'.join(stringhe_da_formattare))

# pivot per il grafico: una riga per utente, una colonna per fascia, più il totale come etichetta numerica

df_pivot = df_definitivo.pivot(index=['id_utente', 'nome'], columns='fascia', values='importo').reset_index()
df_pivot['importo_totale'] = df_pivot[['F1', 'F2', 'F3']].sum(axis=1)

df_bottom = df_pivot[['F1', 'F2', 'F3']].cumsum(axis=1).shift(1, axis=1, fill_value=0)

# due cicli fratelli, allo stesso livello: uno disegna le barre (3 giri, uno per fascia),
# l'altro scrive le etichette (3 giri, uno per utente) - annidarli avrebbe ripetuto le etichette 3 volte

for fascia in df_pivot[['F1', 'F2', 'F3']]:
    plt.bar(x=df_pivot['nome'], height=df_pivot[fascia], bottom=df_bottom[fascia], label=fascia)
for indice, riga in df_pivot.iterrows():
    plt.text(riga['nome'], riga['importo_totale'], f"{riga['importo_totale']:.2f}")
plt.legend()
plt.savefig('img/bar_chart.png')
plt.show()