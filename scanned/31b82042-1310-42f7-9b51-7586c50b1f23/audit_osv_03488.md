# [H] ALPINE-CVE-2026-2007

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-2007
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-2007
Type: osv

## Affected
- Alpine:v3.20: `postgresql15` — affected >=0 <15.17-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.13-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.13-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.13-r0
- Alpine:v3.21: `postgresql17` — affected >=0 <17.9-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.9-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.9-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.9-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.2-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.2-r0

## Details
Heap buffer overflow in PostgreSQL pg_trgm allows a database user to achieve unknown impacts via a crafted input string.  The attacker has limited control over the byte patterns to be written, but we have not ruled out the viability of attacks that lead to privilege escalation.  PostgreSQL 18.1 and 18.0 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-2007
