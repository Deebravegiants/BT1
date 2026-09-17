# [H] ALPINE-CVE-2026-6477

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-6477
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6477
Type: osv

## Affected
- Alpine:v3.20: `postgresql15` — affected >=0 <15.18-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.14-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.10-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.4-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.4-r0

## Details
Use of inherently dangerous function PQfn(..., result_is_int=0, ...) in PostgreSQL libpq lo_export(), lo_read(), lo_lseek64(), and lo_tell64() functions allows the server superuser to overwrite a client stack buffer with an arbitrarily-large response.  Like gets(), PQfn(..., result_is_int=0, ...) stores arbitrary-length, server-determined data into a buffer of unspecified size.  Because both the \lo_export command in psql and pg_dump call lo_read(), the server superuser can overwrite pg_dump or psql stack memory.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6477
