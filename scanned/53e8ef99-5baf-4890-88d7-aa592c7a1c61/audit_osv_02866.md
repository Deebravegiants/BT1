# [M] ALPINE-CVE-2023-39418

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-39418
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-39418
Type: osv

## Affected
- Alpine:v3.13: `postgresql` — affected >=15.0 <13.12-r0
- Alpine:v3.14: `postgresql` — affected >=15.0 <13.12-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.12-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.12-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <14.9-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.9-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.9-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.9-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <15.4-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.4-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.4-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.4-r0

## Details
A vulnerability was found in PostgreSQL with the use of the MERGE command, which fails to test new rows against row security policies defined for UPDATE and SELECT. If UPDATE and SELECT policies forbid some rows that INSERT policies do not forbid, a user could store such rows.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-39418
