# [H] ALPINE-CVE-2017-3145

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-3145
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3145
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.11: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.12: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.13: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.14: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.15: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.16: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.17: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.18: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.19: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.20: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.21: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.22: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.23: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.24: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.4: `bind` — affected >=9.4.0 <9.10.6_p1-r0
- Alpine:v3.5: `bind` — affected >=9.4.0 <9.10.6_p1-r0
- Alpine:v3.6: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.7: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.8: `bind` — affected >=9.4.0 <9.11.2_p1-r0
- Alpine:v3.9: `bind` — affected >=9.4.0 <9.11.2_p1-r0

## Details
BIND was improperly sequencing cleanup operations on upstream recursion fetch contexts, leading in some cases to a use-after-free error that can trigger an assertion failure and crash in named. Affects BIND 9.0.0 to 9.8.x, 9.9.0 to 9.9.11, 9.10.0 to 9.10.6, 9.11.0 to 9.11.2, 9.9.3-S1 to 9.9.11-S1, 9.10.5-S1 to 9.10.6-S1, 9.12.0a1 to 9.12.0rc1.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3145
