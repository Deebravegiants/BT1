# [M] ALPINE-CVE-2021-20227

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-20227
Ecosystem: Alpine:v3.12, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20227
Type: osv

## Affected
- Alpine:v3.12: `sqlite` — affected >=3.33.0 <3.32.1-r1
- Alpine:v3.14: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.15: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.16: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.17: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.18: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.19: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.20: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.21: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.22: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.23: `sqlite` — affected >=3.33.0 <3.34.1-r0
- Alpine:v3.24: `sqlite` — affected >=3.33.0 <3.34.1-r0

## Details
A flaw was found in SQLite's SELECT query functionality (src/select.c). This flaw allows an attacker who is capable of running SQL queries locally on the SQLite database to cause a denial of service or possible code execution by triggering a use-after-free. The highest threat from this vulnerability is to system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20227
