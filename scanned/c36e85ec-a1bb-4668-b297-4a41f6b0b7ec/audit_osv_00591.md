# [C] ALPINE-CVE-2017-17663

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-17663
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17663
Type: osv

## Affected
- Alpine:v3.10: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.11: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.12: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.13: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.14: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.15: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.16: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.17: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.18: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.19: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.20: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.21: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.22: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.23: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.24: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.8: `mini_httpd` — affected >=0 <1.29-r0
- Alpine:v3.9: `mini_httpd` — affected >=0 <1.29-r0

## Details
The htpasswd implementation of mini_httpd before v1.28 and of thttpd before v2.28 is affected by a buffer overflow that can be exploited remotely to perform code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17663
