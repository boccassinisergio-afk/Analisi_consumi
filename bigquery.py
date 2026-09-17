# inizializzazione bigquery
# da utilizzare sempre ad ogni script che interagisce con bigquery

from google.cloud import bigquery

client = bigquery.Client()

with open('queries/00_create_tables.sql', 'r') as file:
    contenuto = file.read()
    create_tables = client.query(contenuto)
    result = create_tables.result()
    
# creo il riferimento al dataset e dopo lo recupero con get_dataset

dataset_ref = client.dataset('energia_consumi')

dataset = client.get_dataset(dataset_ref)

# creo riferimento alle tabelle e poi le recupero

table_ref_uno = dataset_ref.table('utenti')
table_ref_due = dataset_ref.table('consumi')
table_ref_tre = dataset_ref.table('tariffe')

table_uno = client.get_table(table_ref_uno)
table_due = client.get_table(table_ref_due)
table_tre = client.get_table(table_ref_tre)

# stampo lo schema per verificare che non contengano NULL e che sia tutto coerente

print(table_uno.schema, table_due.schema, table_tre.schema)

for field in table_uno.schema:
    print(field.name, field.field_type, field.mode)
for field in table_due.schema:
    print(field.name, field.field_type, field.mode)
for field in table_tre.schema:
    print(field.name, field.field_type, field.mode)
    