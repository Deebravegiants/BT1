# [M] ALPINE-CVE-2023-52722

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-52722
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-52722
Type: osv

## Affected
- Alpine:v3.18: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <10.03.1-r0

## Details
An issue was discovered in Artifex Ghostscript before 10.03.1. psi/zmisc1.c, when SAFER mode is used, allows eexec seeds other than the Type 1 standard.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-52722
