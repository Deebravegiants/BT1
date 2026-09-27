# [H] BIT-postgresql-2023-2454

## Summary
Severity: High
Advisory: BIT-postgresql-2023-2454
Aliases: CVE-2023-2454
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2023-2454
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=15.0.0 <15.3.0

## Details
schema_element defeats protective search_path changes; It was found that certain database calls in PostgreSQL could permit an authed attacker with elevated database-level privileges to execute arbitrary code.

## References
- https://access.redhat.com/security/cve/CVE-2023-2454
- https://security.netapp.com/advisory/ntap-20230706-0006/
- https://www.postgresql.org/support/security/CVE-2023-2454/
- https://nvd.nist.gov/vuln/detail/CVE-2023-2454
