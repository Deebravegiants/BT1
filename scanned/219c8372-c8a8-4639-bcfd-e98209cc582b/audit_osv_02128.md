# [H] ALPINE-CVE-2021-26712

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-26712
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-26712
Type: osv

## Affected
- Alpine:v3.12: `asterisk` — affected >=13.0.0 <16.16.1-r0
- Alpine:v3.13: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.14: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.15: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.16: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.17: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.18: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.19: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.20: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.21: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.22: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.23: `asterisk` — affected >=13.0.0 <18.2.1-r0
- Alpine:v3.24: `asterisk` — affected >=13.0.0 <18.2.1-r0

## Details
Incorrect access controls in res_srtp.c in Sangoma Asterisk 13.38.1, 16.16.0, 17.9.1, and 18.2.0 and Certified Asterisk 16.8-cert5 allow a remote unauthenticated attacker to prematurely terminate secure calls by replaying SRTP packets.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-26712
