import os

with open('prova.txt', 'r') as file:
    contenuto = file.read().split(';')
    lista = [string.strip() for string in contenuto if string]
print(f"{lista}\n ciao")