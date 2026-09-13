# [M] ALPINE-CVE-2021-24031

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-24031
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-24031
Type: osv

## Affected
- Alpine:v3.14: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.15: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.16: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.17: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.18: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.19: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.20: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.21: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.22: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.23: `zstd` — affected >=0 <1.4.1-r0
- Alpine:v3.24: `zstd` — affected >=0 <1.4.1-r0

## Details
In the Zstandard command-line utility prior to v1.4.1, output files were created with default permissions. Correct file permissions (matching the input) would only be set at completion time. Output files could therefore be readable or writable to unintended parties.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-24031
