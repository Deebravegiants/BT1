# [H] ALPINE-CVE-2019-15639

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-15639
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15639
Type: osv

## Affected
- Alpine:v3.11: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.12: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.13: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.14: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.15: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.16: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.17: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.18: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.19: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.20: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.21: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.22: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.23: `asterisk` — affected >=13.0.0 <16.5.1-r0
- Alpine:v3.24: `asterisk` — affected >=13.0.0 <16.5.1-r0

## Details
main/translate.c in Sangoma Asterisk 13.28.0 and 16.5.0 allows a remote attacker to send a specific RTP packet during a call and cause a crash in a specific scenario.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15639
