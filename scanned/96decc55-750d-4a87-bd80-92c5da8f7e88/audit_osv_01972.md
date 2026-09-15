# [M] ALPINE-CVE-2020-35652

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-35652
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35652
Type: osv

## Affected
- Alpine:v3.12: `asterisk` — affected >=14.0 <16.15.1-r0
- Alpine:v3.13: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.14: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.15: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.16: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.17: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.18: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.19: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.20: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.21: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.22: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.23: `asterisk` — affected >=14.0 <18.1.1-r0
- Alpine:v3.24: `asterisk` — affected >=14.0 <18.1.1-r0

## Details
An issue was discovered in res_pjsip_diversion.c in Sangoma Asterisk before 13.38.0, 14.x through 16.x before 16.15.0, 17.x before 17.9.0, and 18.x before 18.1.0. A crash can occur when a SIP message is received with a History-Info header that contains a tel-uri, or when a SIP 181 response is received that contains a tel-uri in the Diversion header.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35652
