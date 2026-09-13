# [M] ALPINE-CVE-2019-15297

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-15297
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15297
Type: osv

## Affected
- Alpine:v3.10: `asterisk` — affected >=15.0.0 <16.3.0-r2
- Alpine:v3.11: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.12: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.13: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.14: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.15: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.16: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.17: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.18: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.19: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.20: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.21: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.22: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.23: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.24: `asterisk` — affected >=15.0.0 <16.5.1-r0
- Alpine:v3.7: `asterisk` — affected >=15.0.0 <15.6.2-r0
- Alpine:v3.8: `asterisk` — affected >=15.0.0 <15.6.2-r0
- Alpine:v3.9: `asterisk` — affected >=15.0.0 <15.7.4-r0

## Details
res_pjsip_t38 in Sangoma Asterisk 15.x before 15.7.4 and 16.x before 16.5.1 allows an attacker to trigger a crash by sending a declined stream in a response to a T.38 re-invite initiated by Asterisk. The crash occurs because of a NULL session media object dereference.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15297
