# [H] ALPINE-CVE-2019-5018

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-5018
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-5018
Type: osv

## Affected
- Alpine:v3.10: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.11: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.12: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.13: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.14: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.15: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.16: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.17: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.18: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.19: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.20: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.21: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.22: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.23: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.24: `sqlite` — affected >=0 <3.28.0-r0
- Alpine:v3.9: `sqlite` — affected >=0 <3.28.0-r0

## Details
An exploitable use after free vulnerability exists in the window function functionality of Sqlite3 3.26.0. A specially crafted SQL command can cause a use after free vulnerability, potentially resulting in remote code execution. An attacker can send a malicious SQL command to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-5018
