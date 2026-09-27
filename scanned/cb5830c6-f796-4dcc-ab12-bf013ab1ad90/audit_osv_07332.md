# [H] PostgreSQL quoting APIs miss neutralizing quoting syntax in text that fails encoding validation

## Summary
Severity: High
Advisory: BIT-postgresql-2025-1094
Aliases: CVE-2025-1094
Ecosystem: Bitnami
Published: 2025-02-17
Source: https://osv.dev/vulnerability/BIT-postgresql-2025-1094
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=17.0.0 <17.3.0

## Details
Improper neutralization of quoting syntax in PostgreSQL libpq functions PQescapeLiteral(), PQescapeIdentifier(), PQescapeString(), and PQescapeStringConn() allows a database input provider to achieve SQL injection in certain usage patterns.  Specifically, SQL injection requires the application to use the function result to construct input to psql, the PostgreSQL interactive terminal.  Similarly, improper neutralization of quoting syntax in PostgreSQL command line utility programs allows a source of command line arguments to achieve SQL injection when client_encoding is BIG5 and server_encoding is one of EUC_TW or MULE_INTERNAL.  Versions before PostgreSQL 17.3, 16.7, 15.11, 14.16, and 13.19 are affected.

## References
- https://www.postgresql.org/support/security/CVE-2025-1094/
- http://www.openwall.com/lists/oss-security/2025/02/16/3
- https://lists.debian.org/debian-lts-announce/2025/02/msg00015.html
- http://www.openwall.com/lists/oss-security/2025/02/20/1
- https://lists.debian.org/debian-lts-announce/2025/02/msg00024.html
- https://security.netapp.com/advisory/ntap-20250221-0010/
- https://nvd.nist.gov/vuln/detail/CVE-2025-1094
