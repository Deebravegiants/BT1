# [M] ALPINE-CVE-2025-4207

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-4207
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-4207
Type: osv

## Affected
- Alpine:v3.18: `postgresql14` — affected >=0 <14.18-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.13-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.13-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.13-r0
- Alpine:v3.19: `postgresql16` — affected >=0 <16.9-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.9-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.9-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.9-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.5-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.5-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.5-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.5-r0

## Details
Buffer over-read in PostgreSQL GB18030 encoding validation allows a database input provider to achieve temporary denial of service on platforms where a 1-byte over-read can elicit process termination.  This affects the database server and also libpq.  Versions before PostgreSQL 17.5, 16.9, 15.13, 14.18, and 13.21 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-4207
