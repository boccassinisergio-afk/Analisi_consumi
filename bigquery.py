# inizializzazione bigquery
# da utilizzare sempre ad ogni script che interagisce con bigquery

import pyplot from matplotlib as plt
import pandas as pd
from google.cloud import bigquery

client = bigquery.Client()

# apro il file per creare dataset e tabelle, attendo il risultato .result() per evitare che lo script avanzi prima della creazione del dataset

with open('queries/00_create_tables.sql', 'r') as file:
    contenuto = file.read()
    create_tables = client.query(contenuto)
    result = create_tables.result()
    
# creo il riferimento al dataset e dopo lo recupero con get_dataset

dataset_ref = client.dataset('energia_consumi')

dataset = client.get_dataset(dataset_ref)
    
# apro il file delle queries, splitto con ; per separare le due SELECT presenti e ripulisco i risultati, assegnando poi a due DF

with open('queries/01_analisi_consumi_e_prezzi.sql', 'r') as file:
    
    contenuto = file.read().split(';')
    queries_ripulite = [stringa.strip() for stringa in contenuto if stringa.strip()]
    
df_picco = client.query(queries_ripulite[0]).result().to_dataframe()
df_fascia = client.query(queries_ripulite[1]).result().to_dataframe()

# totale kWh e importo per ogni combinazione utente+fascia

df_bolletta = df_picco.groupby(['id_utente', 'fascia']).agg({'kwh_consumati':'sum', 'importo':'sum'}).reset_index()
df_pulito = df_picco[['id_utente', 'kwh_picco']].drop_duplicates(subset=['id_utente'])

# merge tra i primi due DF

df_temp = df_bolletta.merge(df_pulito, on='id_utente')

#rinomino le colonne con nomi ambigui che potrebbero causare conflitti prima di fare il secondo merge

df_fascia.rename(columns={'fascia':'fascia_piu_costosa','importo':'importo_fascia_piu_costosa', 'consumo':'kwh_fascia_piu_costosa'}, inplace=True)

# merge definitivo

df_definitivo = df_temp.merge(df_fascia, on='id_utente')

# creo il report vero e proprio iterando su df_definitivo per stampare un blocco per ogni utente
# il primo for crea un id per ogni utente e un unica riga contenente tutte le info in unico blocco
# es. (101,    id_utente fascia  kwh_consumati  importo  kwh_picco fascia_piu_costosa  importo_fascia_piu_costosa  kwh_fascia_piu_costosa 0  101  F1 ...)
# il secondo for itera su ogni riga di ogni utente accedendo ai singoli valori

stringhe_da_formattare = []

for id, gruppo in df_definitivo.groupby('id_utente'):
    stringa_singola = f'Utente {id}\n'
    
    for indice, riga in gruppo.iterrows():
        stringa_singola += f"Fascia {riga['fascia']}: {riga['kwh_consumati']:.2f} → €{riga['importo']:.2f}\n\n"
    
    stringa_singola += f"Picco di consumo: {gruppo['kwh_picco'].iloc[0]:.2f} kwh\nFascia più costosa: {gruppo['fascia_piu_costosa'].iloc[0]} → €{gruppo['importo_fascia_piu_costosa'].iloc[0]:.2f}"    
        
    stringhe_da_formattare.append(stringa_singola)
    
print('\n\n'.join(stringhe_da_formattare))    
                
# con gruppo['kwh_picco'].iloc[0]: prima seleziono la colonna per nome (leggibile, esplicito), poi prendo il primo valore per posizione, 
# essendo valori uguali e ripetuti per ogni riga singola dello stesso utente

# creo una copia del df con .pivot per la generazione del grafico tenendo solo i valori che mi servono + nuova col 'importo_totale'
# columns= colonna da spacchettare in piu colonne dal df originale, values= colonna che fornisce valori da mettere in griglia

df_pivot = df_definitivo.pivot(index=['id_utente', 'nome'], columns='fascia', values='importo').reset_index()

# aggiungo colonna col il totale, mi servira' da inviare alla griglia come etichetta numerica
# axis=1 indica di sommare per righe, non per colonna come di default (axis=0)

df_pivot['importo_totale'] = df_pivot[['F1', 'F2', 'F3']].sum(axis=1)

df_bottom = df_pivot[['F1', 'F2', 'F3']].cumsum(axis=1).shift(1, axis=1, fill_value=0)

# due cicli fratelli, allo stesso livello, uno che disegna le barre (3 giri, uno per fascia) 
# e uno separato che scrive le etichette (3 giri, uno per utente, senza ripetizioni)

for fascia in df_pivot[['F1', 'F2', 'F3']]:
    plt.bar(x=df_pivot['nome'], height=df_pivot[fascia], bottom=df_bottom[fascia], label=fascia)
for indice, riga in df_pivot.iterrows():
    plt.text(riga['nome'], riga['importo_totale'], f"{riga['importo_totale']:.2f}")
plt.legend()
plt.savefig('bar_chart.png')
plt.show()
    