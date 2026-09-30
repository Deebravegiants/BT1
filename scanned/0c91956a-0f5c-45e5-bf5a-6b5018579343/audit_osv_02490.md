# [H] ALPINE-CVE-2022-27239

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-27239
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27239
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
In cifs-utils through 6.14, a stack-based buffer overflow when parsing the mount.cifs ip= command-line argument could lead to local attackers gaining root privileges.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27239
