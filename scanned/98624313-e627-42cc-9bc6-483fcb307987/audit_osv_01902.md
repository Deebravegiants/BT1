# [H] ALPINE-CVE-2020-25695

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25695
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25695
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.6.0 <11.10-r0
- Alpine:v3.11: `postgresql` — affected >=9.6.0 <12.5-r0
- Alpine:v3.12: `postgresql` — affected >=9.6.0 <12.5-r0
- Alpine:v3.13: `postgresql` — affected >=9.6.0 <12.5-r0
- Alpine:v3.14: `postgresql` — affected >=9.6.0 <12.5-r0
- Alpine:v3.9: `postgresql` — affected >=9.6.0 <11.10-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <12.5-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <12.5-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <12.5-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <12.5-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <12.5-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <12.5-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <12.5-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <12.5-r0

## Details
A flaw was found in PostgreSQL versions before 13.1, before 12.5, before 11.10, before 10.15, before 9.6.20 and before 9.5.24. An attacker having permission to create non-temporary objects in at least one schema can execute arbitrary SQL functions under the identity of a superuser. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25695
