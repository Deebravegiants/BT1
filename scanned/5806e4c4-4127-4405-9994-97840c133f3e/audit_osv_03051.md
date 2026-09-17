# [M] ALPINE-CVE-2024-33869

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-33869
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-33869
Type: osv

## Affected
- Alpine:v3.18: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <10.03.1-r0

## Details
An issue was discovered in Artifex Ghostscript before 10.03.1. Path traversal and command execution can occur (via a crafted PostScript document) because of path reduction in base/gpmisc.c. For example, restrictions on use of %pipe% can be bypassed via the aa/../%pipe%command# output filename.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-33869
