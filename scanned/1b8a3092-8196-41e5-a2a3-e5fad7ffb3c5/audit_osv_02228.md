# [M] ALPINE-CVE-2021-3393

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3393
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-04-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3393
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=12.0 <11.11-r0
- Alpine:v3.11: `postgresql` — affected >=12.0 <12.6-r0
- Alpine:v3.12: `postgresql` — affected >=12.0 <12.6-r0
- Alpine:v3.13: `postgresql` — affected >=12.0 <13.2-r0
- Alpine:v3.14: `postgresql` — affected >=12.0 <13.2-r0
- Alpine:v3.9: `postgresql` — affected >=12.0 <11.11-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.2-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.2-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <13.2-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <13.2-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <13.2-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <13.2-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <13.2-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <13.2-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <13.2-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <13.2-r0

## Details
An information leak was discovered in postgresql in versions before 13.2, before 12.6 and before 11.11. A user having UPDATE permission but not SELECT permission to a particular column could craft queries which, under some circumstances, might disclose values from that column in error messages. An attacker could use this flaw to obtain information stored in a column they are allowed to write but not read.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3393
