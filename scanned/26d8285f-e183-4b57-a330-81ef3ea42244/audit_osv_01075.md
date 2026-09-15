# [H] ALPINE-CVE-2018-19278

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-19278
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19278
Type: osv

## Affected
- Alpine:v3.10: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.11: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.12: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.13: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.14: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.15: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.16: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.17: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.18: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.19: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.20: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.21: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.22: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.23: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.24: `asterisk` — affected >=0 <15.7.1-r0
- Alpine:v3.7: `asterisk` — affected >=0 <15.6.2-r0
- Alpine:v3.8: `asterisk` — affected >=0 <15.6.2-r0
- Alpine:v3.9: `asterisk` — affected >=0 <15.7.1-r0

## Details
Buffer overflow in DNS SRV and NAPTR lookups in Digium Asterisk 15.x before 15.6.2 and 16.x before 16.0.1 allows remote attackers to crash Asterisk via a specially crafted DNS SRV or NAPTR response, because a buffer size is supposed to match an expanded length but actually matches a compressed length.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19278
