# [H] ALPINE-CVE-2018-20843

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20843
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20843
Type: osv

## Affected
- Alpine:v3.10: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.11: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.12: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.13: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.14: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.15: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.16: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.17: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.18: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.19: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.20: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.21: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.22: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.23: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.24: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.7: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.8: `expat` — affected >=0 <2.2.7-r0
- Alpine:v3.9: `expat` — affected >=0 <2.2.7-r0

## Details
In libexpat in Expat before 2.2.7, XML input including XML names that contain a large number of colons could make the XML parser consume a high amount of RAM and CPU resources while processing (enough to be usable for denial-of-service attacks).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20843
