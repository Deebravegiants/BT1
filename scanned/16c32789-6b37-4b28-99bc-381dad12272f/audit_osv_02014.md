# [H] ALPINE-CVE-2020-8277

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8277
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8277
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.20.1-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.20.1-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.15.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.15.1-r0

## Details
A Node.js application that allows an attacker to trigger a DNS request for a host of their choice could trigger a Denial of Service in versions < 15.2.1, < 14.15.1, and < 12.19.1 by getting the application to resolve a DNS record with a larger number of responses. This is fixed in 15.2.1, 14.15.1, and 12.19.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8277
