CREATE SCHEMA IF NOT EXISTS energia_consumi;

CREATE OR REPLACE TABLE energia_consumi.utenti (id_utente INT64 PRIMARY KEY NOT ENFORCED, nome STRING );

CREATE OR REPLACE TABLE energia_consumi.consumi (id_consumo INT64 PRIMARY KEY NOT ENFORCED, id_utente INT64, timestamp TIMESTAMP, kwh_consumati NUMERIC, CONSTRAINT fk_consumi_utenti FOREIGN KEY (id_utente) REFERENCES energia_consumi.utenti(id_utente) NOT ENFORCED);

CREATE OR REPLACE TABLE energia_consumi.tariffe (fascia STRING PRIMARY KEY NOT ENFORCED, ora_inizio INT64, ora_fine INT64, costo_kwh NUMERIC);

INSERT INTO energia_consumi.utenti ( id_utente, nome ) VALUES (1, 'Sergio Rossi'), (2, 'Mariantonia Verdi'), (3, 'Rosanna Bianchi');
INSERT INTO energia_consumi.consumi ( id_consumo, id_utente, timestamp, kwh_consumati ) VALUES (1, 1, '2026-01-05 07:15:00', 0.8),
(2, 1, '2026-01-05 13:40:00', 1.2),
(3, 1, '2026-01-05 19:20:00', 2.1),
(4, 1, '2026-01-05 02:10:00', 0.5),
(5, 2, '2026-01-05 08:00:00', 0.6),
(6, 2, '2026-01-05 14:15:00', 0.9),
(7, 2, '2026-01-05 20:45:00', 1.7),
(8, 2, '2026-01-05 01:30:00', 0.4),
(9, 3, '2026-01-05 06:50:00', 1.0),
(10, 3, '2026-01-05 12:30:00', 1.5),
(11, 3, '2026-01-05 18:10:00', 2.4),
(12, 3, '2026-01-05 23:50:00', 0.7);
INSERT INTO energia_consumi.tariffe ( fascia, ora_inizio, ora_fine, costo_kwh ) VALUES ('F1', 6, 15, 0.15), ('F2', 15, 23, 0.12), ('F3', 23, 6, 0.09);

