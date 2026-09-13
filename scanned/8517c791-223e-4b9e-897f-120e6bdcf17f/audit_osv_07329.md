# [C] BIT-postgresql-2024-24213

## Summary
Severity: Critical
Advisory: BIT-postgresql-2024-24213
Aliases: CVE-2024-24213
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2024-24213
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=15.1.0

## Details
Supabase PostgreSQL v15.1 was discovered to contain a SQL injection vulnerability via the component /pg_meta/default/query. NOTE: the vendor's position is that this is an intended feature; also, it exists in the Supabase dashboard product, not the Supabase PostgreSQL product. Specifically, /pg_meta/default/query is for SQL queries that are entered in an intended UI by an authorized user. Nothing is injected.

## References
- https://app.flows.sh:8443/project/default%2C
- https://github.com/940198871/Vulnerability-details/blob/main/CVE-2024-24213
- https://postfixadmin.ballardini.com.ar:8443/project/default/logs/explorer.
- https://reference1.example.com/project/default/logs/explorer%2C
- https://supabase.com/docs/guides/database/overview#the-sql-editor
