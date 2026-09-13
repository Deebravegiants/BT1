# [M] ALPINE-CVE-2020-8315

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-8315
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8315
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
In Python (CPython) 3.6 through 3.6.10, 3.7 through 3.7.6, and 3.8 through 3.8.1, an insecure dependency load upon launch on Windows 7 may result in an attacker's copy of api-ms-win-core-path-l1-1-0.dll being loaded and used instead of the system's copy. Windows 8 and later are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8315
