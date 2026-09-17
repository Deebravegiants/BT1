# [H] ALPINE-CVE-2025-1094

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-1094
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-1094
Type: osv

## Affected
- Alpine:v3.18: `postgresql14` — affected >=0 <14.17-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.11-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.11-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.11-r0
- Alpine:v3.19: `postgresql16` — affected >=0 <16.8-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.8-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.8-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.8-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.4-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.4-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.4-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.4-r0

## Details
Improper neutralization of quoting syntax in PostgreSQL libpq functions PQescapeLiteral(), PQescapeIdentifier(), PQescapeString(), and PQescapeStringConn() allows a database input provider to achieve SQL injection in certain usage patterns.  Specifically, SQL injection requires the application to use the function result to construct input to psql, the PostgreSQL interactive terminal.  Similarly, improper neutralization of quoting syntax in PostgreSQL command line utility programs allows a source of command line arguments to achieve SQL injection when client_encoding is BIG5 and server_encoding is one of EUC_TW or MULE_INTERNAL.  Versions before PostgreSQL 17.3, 16.7, 15.11, 14.16, and 13.19 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-1094
