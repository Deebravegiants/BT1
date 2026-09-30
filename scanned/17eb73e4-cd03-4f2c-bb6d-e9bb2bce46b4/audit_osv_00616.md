# [M] ALPINE-CVE-2017-3138

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3138
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3138
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
named contains a feature which allows operators to issue commands to a running server by communicating with the server process over a control channel, using a utility program such as rndc. A regression introduced in a recent feature change has created a situation under which some versions of named can be caused to exit with a REQUIRE assertion failure if they are sent a null command string. Affects BIND 9.9.9->9.9.9-P7, 9.9.10b1->9.9.10rc2, 9.10.4->9.10.4-P7, 9.10.5b1->9.10.5rc2, 9.11.0->9.11.0-P4, 9.11.1b1->9.11.1rc2, 9.9.9-S1->9.9.9-S9.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3138
