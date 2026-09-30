# [M] ALPINE-CVE-2020-35776

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-35776
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35776
Type: osv

## Affected
- Alpine:v3.12: `asterisk` — affected >=13.0.0 <16.16.1-r0
- Alpine:v3.13: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.14: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.15: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.16: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.17: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.18: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.19: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.20: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.21: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.22: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.23: `asterisk` — affected >=13.0.0 <18.1.1-r0
- Alpine:v3.24: `asterisk` — affected >=13.0.0 <18.1.1-r0

## Details
A buffer overflow in res_pjsip_diversion.c in Sangoma Asterisk versions 13.38.1, 16.15.1, 17.9.1, and 18.1.1 allows remote attacker to crash Asterisk by deliberately misusing SIP 181 responses.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35776
