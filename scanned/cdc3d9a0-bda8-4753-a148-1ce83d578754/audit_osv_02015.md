# [H] ALPINE-CVE-2020-8285

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8285
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8285
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.66.0-r3
- Alpine:v3.11: `curl` — affected >=0 <7.67.0-r3
- Alpine:v3.12: `curl` — affected >=0 <7.69.1-r3
- Alpine:v3.13: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.74.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.74.0-r0

## Details
curl 7.21.0 to and including 7.73.0 is vulnerable to uncontrolled recursion due to a stack overflow issue in FTP wildcard match parsing.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8285
