# [H] ALPINE-CVE-2019-10143

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10143
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10143
Type: osv

## Affected
- Alpine:v3.10: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.11: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.12: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.13: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.14: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.15: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.16: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.17: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.18: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.19: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.20: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.21: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.22: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.23: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.24: `freeradius` — affected >=0 <3.0.19-r3
- Alpine:v3.7: `freeradius` — affected >=0 <3.0.17-r5
- Alpine:v3.8: `freeradius` — affected >=0 <3.0.17-r4
- Alpine:v3.9: `freeradius` — affected >=0 <3.0.17-r6

## Details
It was discovered freeradius up to and including version 3.0.19 does not correctly configure logrotate, allowing a local attacker who already has control of the radiusd user to escalate his privileges to root, by tricking logrotate into writing a radiusd-writable file to a directory normally inaccessible by the radiusd user. NOTE: the upstream software maintainer has stated "there is simply no way for anyone to gain privileges through this alleged issue."

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10143
