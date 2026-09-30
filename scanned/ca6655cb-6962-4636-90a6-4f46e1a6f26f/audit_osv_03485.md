# [H] ALPINE-CVE-2026-2004

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-2004
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-2004
Type: osv

## Affected
- Alpine:v3.20: `postgresql15` — affected >=0 <15.16-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.12-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.12-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.12-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.8-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.8-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.8-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.8-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.2-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.2-r0

## Details
Missing validation of type of input in PostgreSQL intarray extension selectivity estimator function allows an object creator to execute arbitrary code as the operating system user running the database.  Versions before PostgreSQL 18.2, 17.8, 16.12, 15.16, and 14.21 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-2004
