# [H] ALPINE-CVE-2021-32558

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-32558
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32558
Type: osv

## Affected
- Alpine:v3.11: `asterisk` — affected >=13.0.0 <16.6.2-r1
- Alpine:v3.12: `asterisk` — affected >=13.0.0 <16.16.1-r1
- Alpine:v3.13: `asterisk` — affected >=13.0.0 <18.2.1-r2
- Alpine:v3.14: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.15: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.16: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.17: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.18: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.19: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.20: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.21: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.22: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.23: `asterisk` — affected >=13.0.0 <18.2.2-r2
- Alpine:v3.24: `asterisk` — affected >=13.0.0 <18.2.2-r2

## Details
An issue was discovered in Sangoma Asterisk 13.x before 13.38.3, 16.x before 16.19.1, 17.x before 17.9.4, and 18.x before 18.5.1, and Certified Asterisk before 16.8-cert10. If the IAX2 channel driver receives a packet that contains an unsupported media format, a crash can occur.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32558
