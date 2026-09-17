SELECT
    c.id_consumo,
    c.id_utente,
    c.timestamp,
    c.kwh_consumati,
    t.fascia,
    t.costo_kwh,
    c.kwh_consumati * t.costo_kwh AS importo,
    MAX(c.kwh_consumati) OVER(PARTITION BY c.id_utente) AS kwh_picco
FROM energia_consumi.consumi AS c
LEFT JOIN energia_consumi.tariffe AS t
    ON (
        (
            t.ora_inizio < t.ora_fine
            AND EXTRACT(HOUR FROM c.timestamp) >= t.ora_inizio
            AND EXTRACT(HOUR FROM c.timestamp) < t.ora_fine
        )
        OR
        (
            t.ora_inizio > t.ora_fine
            AND (
                EXTRACT(HOUR FROM c.timestamp) >= t.ora_inizio
                OR EXTRACT(HOUR FROM c.timestamp) < t.ora_fine
            )
        )
    );

WITH costi_per_fascia AS (
    SELECT
        c.id_utente,
        t.fascia,
        SUM(c.kwh_consumati * t.costo_kwh) AS importo
    FROM energia_consumi.consumi AS c
    LEFT JOIN energia_consumi.tariffe AS t 
        ON (
            (
                t.ora_inizio < t.ora_fine
                AND EXTRACT(HOUR FROM c.timestamp) >= t.ora_inizio
                AND EXTRACT(HOUR FROM c.timestamp) < t.ora_fine
            )
            OR
            (
                t.ora_inizio > t.ora_fine
                AND (
                    EXTRACT(HOUR FROM c.timestamp) >= t.ora_inizio
                    OR EXTRACT(HOUR FROM c.timestamp) < t.ora_fine
                )
            )
        )
    GROUP BY 
        c.id_utente,
        t.fascia 
)

SELECT id_utente, fascia, importo
FROM costi_per_fascia
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY id_utente
    ORDER BY importo DESC
) = 1;