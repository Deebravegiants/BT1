# [M] ALPINE-CVE-2026-6474

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-6474
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6474
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
Externally-controlled format string in PostgreSQL timeofday() function allows an attacker to retrieve portions of server memory, via crafted timezone zones.  Versions before PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6474
