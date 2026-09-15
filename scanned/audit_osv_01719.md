# [H] ALPINE-CVE-2020-11655

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-11655
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-11655
Type: osv

## Affected
- Alpine:v3.10: `sqlite` — affected >=0 <3.28.0-r3
- Alpine:v3.11: `sqlite` — affected >=0 <3.30.1-r2
- Alpine:v3.12: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.13: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.14: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.15: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.16: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.17: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.18: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.19: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.20: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.21: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.22: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.23: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.24: `sqlite` — affected >=0 <3.30.1-r3
- Alpine:v3.8: `sqlite` — affected >=0 <3.25.0-r4
- Alpine:v3.9: `sqlite` — affected >=0 <3.28.0-r3

## Details
SQLite through 3.31.1 allows attackers to cause a denial of service (segmentation fault) via a malformed window-function query because the AggInfo object's initialization is mishandled.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-11655
