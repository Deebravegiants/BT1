# [M] ALPINE-CVE-2026-2003

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-2003
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-2003
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
Improper validation of type "oidvector" in PostgreSQL allows a database user to disclose a few bytes of server memory.  We have not ruled out viability of attacks that arrange for presence of confidential information in disclosed bytes, but they seem unlikely.  Versions before PostgreSQL 18.2, 17.8, 16.12, 15.16, and 14.21 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-2003
