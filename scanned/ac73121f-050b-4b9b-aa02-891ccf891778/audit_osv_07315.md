# [M] BIT-postgresql-2021-43767

## Summary
Severity: Medium
Advisory: BIT-postgresql-2021-43767
Aliases: CVE-2021-43767
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2021-43767
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=14.0.0 <14.0.1

## Details
Odyssey passes to client unencrypted bytes from man-in-the-middle When Odyssey storage is configured to use the PostgreSQL server using 'trust' authentication with a 'clientcert' requirement or to use 'cert' authentication, a man-in-the-middle attacker can inject false responses to the client's first few queries. Despite the use of SSL certificate verification and encryption, Odyssey will pass these results to client as if they originated from valid server. This is similar to CVE-2021-23222 for PostgreSQL.

## References
- https://github.com/yandex/odyssey/issues/377%2C
- https://www.postgresql.org/support/security/CVE-2021-23222/
- https://nvd.nist.gov/vuln/detail/CVE-2021-43767
