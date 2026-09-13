# [M] ALPINE-CVE-2020-8492

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-8492
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8492
Type: osv

## Affected
- Alpine:v3.10: `python3` — affected >=0 <3.7.7-r0
- Alpine:v3.11: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.12: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.13: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.14: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.15: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.16: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.17: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.18: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.19: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.20: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.21: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.22: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.23: `python3` — affected >=0 <3.8.2-r0
- Alpine:v3.24: `python3` — affected >=0 <3.8.2-r0

## Details
Python 2.7 through 2.7.17, 3.5 through 3.5.9, 3.6 through 3.6.10, 3.7 through 3.7.6, and 3.8 through 3.8.1 allows an HTTP server to conduct Regular Expression Denial of Service (ReDoS) attacks against a client because of urllib.request.AbstractBasicAuthHandler catastrophic backtracking.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8492
