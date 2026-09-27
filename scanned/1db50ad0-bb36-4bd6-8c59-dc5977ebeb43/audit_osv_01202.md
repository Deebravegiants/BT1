# [H] ALPINE-CVE-2018-5737

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-5737
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5737
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.11: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.12: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.13: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.14: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.15: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.16: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.17: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.18: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.19: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.20: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.21: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.22: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.23: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.24: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.8: `bind` — affected >=0 <9.12.1_p2-r0
- Alpine:v3.9: `bind` — affected >=0 <9.12.1_p2-r0

## Details
A problem with the implementation of the new serve-stale feature in BIND 9.12 can lead to an assertion failure in rbtdb.c, even when stale-answer-enable is off. Additionally, problematic interaction between the serve-stale feature and NSEC aggressive negative caching can in some cases cause undesirable behavior from named, such as a recursion loop or excessive logging. Deliberate exploitation of this condition could cause operational problems depending on the particular manifestation -- either degradation or denial of service. Affects BIND 9.12.0 and 9.12.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5737
