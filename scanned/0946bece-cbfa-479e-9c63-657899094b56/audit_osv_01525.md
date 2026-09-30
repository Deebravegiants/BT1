# [H] ALPINE-CVE-2019-18610

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18610
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18610
Type: osv

## Affected
- Alpine:v3.10: `asterisk` — affected >=13.0.0 <16.3.0-r3
- Alpine:v3.11: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.12: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.13: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.14: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.15: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.16: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.17: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.18: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.19: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.20: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.21: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.22: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.23: `asterisk` — affected >=13.0.0 <16.6.2-r0
- Alpine:v3.24: `asterisk` — affected >=13.0.0 <16.6.2-r0

## Details
An issue was discovered in manager.c in Sangoma Asterisk through 13.x, 16.x, 17.x and Certified Asterisk 13.21 through 13.21-cert4. A remote authenticated Asterisk Manager Interface (AMI) user without system authorization could use a specially crafted Originate AMI request to execute arbitrary system commands.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18610
