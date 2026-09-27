# [H] ALPINE-CVE-2024-0985

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-0985
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-02-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-0985
Type: osv

## Affected
- Alpine:v3.16: `postgresql13` — affected >=0 <13.14-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.11-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.11-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.11-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <15.6-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.6-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.6-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.6-r0
- Alpine:v3.19: `postgresql16` — affected >=0 <16.2-r0
- Alpine:v3.20: `postgresql16` — affected >=0 <16.2-r0
- Alpine:v3.21: `postgresql16` — affected >=0 <16.2-r0
- Alpine:v3.22: `postgresql16` — affected >=0 <16.2-r0

## Details
Late privilege drop in REFRESH MATERIALIZED VIEW CONCURRENTLY in PostgreSQL allows an object creator to execute arbitrary SQL functions as the command issuer. The command intends to run SQL functions as the owner of the materialized view, enabling safe refresh of untrusted materialized views. The victim is a superuser or member of one of the attacker's roles. The attack requires luring the victim into running REFRESH MATERIALIZED VIEW CONCURRENTLY on the attacker's materialized view. Versions before PostgreSQL 16.2, 15.6, 14.11, 13.14, and 12.18 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-0985
