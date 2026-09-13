# [H] ALPINE-CVE-2020-8177

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8177
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8177
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=7.20.0 <7.66.0-r1
- Alpine:v3.11: `curl` — affected >=7.20.0 <7.67.0-r1
- Alpine:v3.12: `curl` — affected >=7.20.0 <7.69.1-r1
- Alpine:v3.13: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.14: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.15: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.16: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.17: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.18: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.19: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.20: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.21: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.22: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.23: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.24: `curl` — affected >=7.20.0 <7.71.0-r0
- Alpine:v3.9: `curl` — affected >=7.20.0 <7.64.0-r4

## Details
curl 7.20.0 through 7.70.0 is vulnerable to improper restriction of names for files and other resources that can lead too overwriting a local file when the -J flag is used.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8177
