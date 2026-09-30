# [H] ALPINE-CVE-2024-7348

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-7348
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-7348
Type: osv

## Affected
- Alpine:v3.17: `postgresql14` — affected >=0 <14.13-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.13-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <15.8-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.8-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.8-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.8-r0
- Alpine:v3.19: `postgresql16` — affected >=0 <16.4-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.4-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.4-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.4-r0

## Details
Time-of-check Time-of-use (TOCTOU) race condition in pg_dump in PostgreSQL allows an object creator to execute arbitrary SQL functions as the user running pg_dump, which is often a superuser. The attack involves replacing another relation type with a view or foreign table. The attack requires waiting for pg_dump to start, but winning the race condition is trivial if the attacker retains an open transaction. Versions before PostgreSQL 16.4, 15.8, 14.13, 13.16, and 12.20 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-7348
