# [M] ALPINE-CVE-2021-22960

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-22960
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-11-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22960
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
The parse function in llhttp < 2.1.4 and < 6.0.6. ignores chunk extensions when parsing the body of chunked requests. This leads to HTTP Request Smuggling (HRS) under certain conditions.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22960
