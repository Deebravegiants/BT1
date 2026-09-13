# [M] ALPINE-CVE-2017-5969

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-5969
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5969
Type: osv

## Affected
- Alpine:v3.10: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.11: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.12: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.13: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.14: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.15: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.16: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.17: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.18: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.19: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.2: `libxml2` — affected >=0 <2.9.4-r3
- Alpine:v3.20: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.21: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.22: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.23: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.24: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.3: `libxml2` — affected >=0 <2.9.4-r3
- Alpine:v3.4: `libxml2` — affected >=0 <2.9.4-r3
- Alpine:v3.5: `libxml2` — affected >=0 <2.9.4-r3
- Alpine:v3.6: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.7: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.8: `libxml2` — affected >=0 <2.9.4-r4
- Alpine:v3.9: `libxml2` — affected >=0 <2.9.4-r4

## Details
libxml2 2.9.4, when used in recover mode, allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted XML document.  NOTE: The maintainer states "I would disagree of a CVE with the Recover parsing option which should only be used for manual recovery at least for XML parser.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5969
