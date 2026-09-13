# [M] ALPINE-CVE-2021-22959

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-22959
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22959
Type: osv

## Affected
- Alpine:v3.12: `nodejs` — affected >=0 <12.22.10-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.18.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.18.1-r0

## Details
The parser in accepts requests with a space (SP) right after the header name before the colon. This can lead to HTTP Request Smuggling (HRS) in llhttp < v2.1.4 and < v6.0.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22959
