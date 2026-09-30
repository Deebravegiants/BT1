# [M] ALPINE-CVE-2021-26906

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-26906
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-26906
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
An issue was discovered in res_pjsip_session.c in Digium Asterisk through 13.38.1; 14.x, 15.x, and 16.x through 16.16.0; 17.x through 17.9.1; and 18.x through 18.2.0, and Certified Asterisk through 16.8-cert5. An SDP negotiation vulnerability in PJSIP allows a remote server to potentially crash Asterisk by sending specific SIP responses that cause an SDP negotiation failure.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-26906
