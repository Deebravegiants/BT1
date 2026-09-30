# [H] ALPINE-CVE-2019-6476

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-6476
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6476
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.11: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.12: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.13: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.14: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.15: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.16: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.17: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.18: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.19: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.20: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.21: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.22: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.23: `bind` — affected >=9.14.0 <9.14.7-r0
- Alpine:v3.24: `bind` — affected >=9.14.0 <9.14.7-r0

## Details
A defect in code added to support QNAME minimization can cause named to exit with an assertion failure if a forwarder returns a referral rather than resolving the query. This affects BIND versions 9.14.0 up to 9.14.6, and 9.15.0 up to 9.15.4.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6476
