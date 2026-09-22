# [H] ALPINE-CVE-2017-3137

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-3137
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3137
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.11: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.12: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.13: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.14: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.15: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.16: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.17: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.18: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.19: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.2: `bind` — affected >=0 <9.10.4_p8
- Alpine:v3.20: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.21: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.22: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.23: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.24: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.3: `bind` — affected >=0 <9.10.4_p8-r0
- Alpine:v3.5: `bind` — affected >=0 <9.10.4_p8-r0
- Alpine:v3.6: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.7: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.8: `bind` — affected >=0 <9.11.0_p5-r0
- Alpine:v3.9: `bind` — affected >=0 <9.11.0_p5-r0

## Details
Mistaken assumptions about the ordering of records in the answer section of a response containing CNAME or DNAME resource records could lead to a situation in which named would exit with an assertion failure when processing a response in which records occurred in an unusual order. Affects BIND 9.9.9-P6, 9.9.10b1->9.9.10rc1, 9.10.4-P6, 9.10.5b1->9.10.5rc1, 9.11.0-P3, 9.11.1b1->9.11.1rc1, and 9.9.9-S8.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3137
