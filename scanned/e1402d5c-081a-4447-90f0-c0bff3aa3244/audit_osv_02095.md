# [M] ALPINE-CVE-2021-22939

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-22939
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-08-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22939
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.22.5-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.22.5-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.17.5-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.17.5-r0

## Details
If the Node.js https API was used incorrectly and "undefined" was in passed for the "rejectUnauthorized" parameter, no error was returned and connections to servers with an expired certificate would have been accepted.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22939
