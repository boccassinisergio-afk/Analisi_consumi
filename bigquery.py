# inizializzazione bigquery
# da utilizzare sempre ad ogni script che interagisce con bigquery

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

for id, gruppo in df_definitivo.groupby('id_utente'):
    for indice, riga in gruppo.iterrows():
        print(f"Utente: {indice}\n Fascia {riga['fascia']}: {riga['kwh_consumati']} → €{riga['importo']}")
        print("")
        print(f"Picco di consumo: {gruppo['kwh_picco'].iloc[0]} kwh")
        print(f"Fascia più costosa: {gruppo['fascia_piu_costosa'].iloc[0]} → € {gruppo['importo_fascia_piu_costosa'].iloc[0]}")
        
        