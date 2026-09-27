# [H] ALPINE-CVE-2024-46956

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-46956
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-46956
Type: osv

## Affected
- Alpine:v3.18: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <10.04.0-r0

## Details
An issue was discovered in psi/zfile.c in Artifex Ghostscript before 10.04.0. Out-of-bounds data access in filenameforall can lead to arbitrary code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-46956
