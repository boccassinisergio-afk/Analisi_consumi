
SELECT c.id_consumo, c.id_utente, c.timestamp, t.fascia, t.costo_kwh, c.kwh_consumati * t.costo_kwh AS importo
FROM consumi AS c LEFT JOIN tariffe AS t
WHERE