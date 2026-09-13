# [M] ALPINE-CVE-2021-29133

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-29133
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-29133
Type: osv

## Affected
- Alpine:v3.10: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.11: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.12: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.13: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.14: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.15: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.16: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.17: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.18: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.19: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.20: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.21: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.22: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.23: `haserl` — affected >=0 <0.9.36-r0
- Alpine:v3.24: `haserl` — affected >=0 <0.9.36-r0

## Details
Lack of verification in haserl, a component of Alpine Linux Configuration Framework, before 0.9.36 allows local users to read the contents of any file on the filesystem.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-29133
