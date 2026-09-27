# [H] ALPINE-CVE-2018-5740

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-5740
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5740
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.11: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.12: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.13: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.14: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.15: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.16: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.17: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.18: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.19: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.20: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.21: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.22: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.23: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.24: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.5: `bind` — affected >=9.7.0 <9.10.8_p1-r0
- Alpine:v3.6: `bind` — affected >=9.7.0 <9.11.4_p1-r0
- Alpine:v3.7: `bind` — affected >=9.7.0 <9.11.4_p1-r0
- Alpine:v3.8: `bind` — affected >=9.7.0 <9.12.2_p1-r0
- Alpine:v3.9: `bind` — affected >=9.7.0 <9.12.2_p1-r0

## Details
"deny-answer-aliases" is a little-used feature intended to help recursive server operators protect end users against DNS rebinding attacks, a potential method of circumventing the security model used by client browsers. However, a defect in this feature makes it easy, when the feature is in use, to experience an assertion failure in name.c. Affects BIND 9.7.0->9.8.8, 9.9.0->9.9.13, 9.10.0->9.10.8, 9.11.0->9.11.4, 9.12.0->9.12.2, 9.13.0->9.13.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5740
