# [H] ALPINE-CVE-2020-14350

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14350
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.9
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14350
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.5 <11.9-r0
- Alpine:v3.11: `postgresql` — affected >=9.5 <12.4-r0
- Alpine:v3.12: `postgresql` — affected >=9.5 <12.4-r0
- Alpine:v3.13: `postgresql` — affected >=9.5 <12.4-r0
- Alpine:v3.14: `postgresql` — affected >=9.5 <12.4-r0
- Alpine:v3.9: `postgresql` — affected >=9.5 <11.9-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <12.4-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <12.4-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <12.4-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <12.4-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <12.4-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <12.4-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <12.4-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <12.4-r0

## Details
It was found that some PostgreSQL extensions did not use search_path safely in their installation script. An attacker with sufficient privileges could use this flaw to trick an administrator into executing a specially crafted script, during the installation or update of such extension. This affects PostgreSQL versions before 12.4, before 11.9, before 10.14, before 9.6.19, and before 9.5.23.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14350
