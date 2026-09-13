# [M] ALPINE-CVE-2021-22923

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-22923
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22923
Type: osv

## Affected
- Alpine:v3.11: `curl` — affected >=7.27.0 <7.79.0-r0
- Alpine:v3.12: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.13: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.14: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.15: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.16: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.17: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.18: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.19: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.20: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.21: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.22: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.23: `curl` — affected >=7.27.0 <7.78.0-r0
- Alpine:v3.24: `curl` — affected >=7.27.0 <7.78.0-r0

## Details
When curl is instructed to get content using the metalink feature, and a user name and password are used to download the metalink XML file, those same credentials are then subsequently passed on to each of the servers from which curl will download or try to download the contents from. Often contrary to the user's expectations and intentions and without telling the user it happened.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22923
