# [M] ALPINE-CVE-2022-42706

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42706
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42706
Type: osv

## Affected
- Alpine:v3.16: `asterisk` — affected >=16.0.0 <18.20.2-r0
- Alpine:v3.17: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.18: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.19: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.20: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.21: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.22: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.23: `asterisk` — affected >=16.0.0 <18.15.1-r0
- Alpine:v3.24: `asterisk` — affected >=16.0.0 <18.15.1-r0

## Details
An issue was discovered in Sangoma Asterisk through 16.28, 17 and 18 through 18.14, 19 through 19.6, and certified through 18.9-cert1. GetConfig, via Asterisk Manager Interface, allows a connected application to access files outside of the asterisk configuration directory, aka Directory Traversal.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42706
