# [H] ALPINE-CVE-2023-2454

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-2454
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-2454
Type: osv

## Affected
- Alpine:v3.13: `postgresql` — affected >=11.0 <13.11-r0
- Alpine:v3.14: `postgresql` — affected >=11.0 <13.11-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.11-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.11-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <14.8-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <14.8-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <14.8-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <14.8-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <15.3-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <15.3-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <15.3-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <15.3-r0

## Details
schema_element defeats protective search_path changes; It was found that certain database calls in PostgreSQL could permit an authed attacker with elevated database-level privileges to execute arbitrary code.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-2454
