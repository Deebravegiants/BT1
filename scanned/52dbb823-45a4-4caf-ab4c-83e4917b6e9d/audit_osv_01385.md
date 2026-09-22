# [M] ALPINE-CVE-2019-12827

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-12827
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12827
Type: osv

## Affected
- Alpine:v3.10: `asterisk` — affected >=13.0.0 <16.3.0-r2
- Alpine:v3.11: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.12: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.13: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.14: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.15: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.16: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.17: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.18: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.19: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.20: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.21: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.22: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.23: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.24: `asterisk` — affected >=13.0.0 <16.4.1-r0
- Alpine:v3.7: `asterisk` — affected >=13.0.0 <15.6.2-r0
- Alpine:v3.8: `asterisk` — affected >=13.0.0 <15.6.2-r0
- Alpine:v3.9: `asterisk` — affected >=13.0.0 <15.7.4-r0

## Details
Buffer overflow in res_pjsip_messaging in Digium Asterisk versions 13.21-cert3, 13.27.0, 15.7.2, 16.4.0 and earlier allows remote authenticated users to crash Asterisk by sending a specially crafted SIP MESSAGE message.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12827
