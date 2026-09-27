# [M] ALPINE-CVE-2022-29869

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-29869
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-04-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-29869
Type: osv

## Affected
- Alpine:v3.16: `cifs-utils` — affected >=0 <6.15-r0
- Alpine:v3.17: `cifs-utils` — affected >=0 <6.15-r0
- Alpine:v3.18: `cifs-utils` — affected >=0 <6.15-r0
- Alpine:v3.19: `cifs-utils` — affected >=0 <6.15-r0
- Alpine:v3.20: `cifs-utils` — affected >=0 <6.15-r0
- Alpine:v3.21: `cifs-utils` — affected >=0 <6.15-r0
- Alpine:v3.22: `cifs-utils` — affected >=0 <6.15-r0
- Alpine:v3.23: `cifs-utils` — affected >=0 <6.15-r0
- Alpine:v3.24: `cifs-utils` — affected >=0 <6.15-r0

## Details
cifs-utils through 6.14, with verbose logging, can cause an information leak when a file contains = (equal sign) characters but is not a valid credentials file.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-29869
