# [C] ALPINE-CVE-2018-7053

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-7053
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7053
Type: osv

## Affected
- Alpine:v3.10: `irssi` — affected >=0 <1.1.1-r0
- Alpine:v3.11: `irssi` — affected >=0 <1.1.1-r0
- Alpine:v3.12: `irssi` — affected >=0 <1.1.1-r0
- Alpine:v3.13: `irssi` — affected >=0 <1.1.1-r0
- Alpine:v3.14: `irssi` — affected >=0 <1.1.1-r0
- Alpine:v3.15: `irssi` — affected >=0 <1.1.1-r0
- Alpine:v3.16: `irssi` — affected >=0 <1.1.1-r0
- Alpine:v3.17: `irssi` — affected >=0 <1.1.1-r0
- Alpine:v3.6: `irssi` — affected >=0 <1.0.6-r0
- Alpine:v3.7: `irssi` — affected >=0 <1.0.6-r0
- Alpine:v3.8: `irssi` — affected >=0 <1.1.1-r0
- Alpine:v3.9: `irssi` — affected >=0 <1.1.1-r0

## Details
An issue was discovered in Irssi before 1.0.7 and 1.1.x before 1.1.1. There is a use-after-free when SASL messages are received in an unexpected order.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7053
