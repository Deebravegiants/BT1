# [H] ALPINE-CVE-2021-32027

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-32027
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32027
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.6.0 <11.12-r0
- Alpine:v3.11: `postgresql` — affected >=9.6.0 <12.7-r0
- Alpine:v3.12: `postgresql` — affected >=9.6.0 <12.7-r0
- Alpine:v3.13: `postgresql` — affected >=9.6.0 <13.3-r0
- Alpine:v3.14: `postgresql` — affected >=9.6.0 <13.3-r0
- Alpine:v3.15: `postgresql13` — affected >=0 <13.3-r0
- Alpine:v3.16: `postgresql13` — affected >=0 <13.3-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <13.3-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <13.3-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <13.3-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <13.3-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <13.3-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <13.3-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <13.3-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <13.3-r0

## Details
A flaw was found in postgresql in versions before 13.3, before 12.7, before 11.12, before 10.17 and before 9.6.22. While modifying certain SQL array values, missing bounds checks let authenticated database users write arbitrary bytes to a wide area of server memory. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32027
