# [H] ALPINE-CVE-2019-20907

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-20907
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20907
Type: osv

## Affected
- Alpine:v3.12: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.13: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.14: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.15: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.16: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.17: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.18: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.19: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.20: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.21: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.22: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.23: `python3` — affected >=0 <3.8.5-r0
- Alpine:v3.24: `python3` — affected >=0 <3.8.5-r0

## Details
In Lib/tarfile.py in Python through 3.8.3, an attacker is able to craft a TAR archive leading to an infinite loop when opened by tarfile.open, because _proc_pax lacks header validation.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20907
