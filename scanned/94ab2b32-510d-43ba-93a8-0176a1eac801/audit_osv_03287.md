# [M] ALPINE-CVE-2025-46646

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-46646
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-04-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-46646
Type: osv

## Affected
- Alpine:v3.18: `ghostscript` — affected >=0 <10.05.1
- Alpine:v3.19: `ghostscript` — affected >=0 <10.05.1-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <10.05.1-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <10.05.1-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <10.05.1-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <10.05.1-r0

## Details
In Artifex Ghostscript before 10.05.0, decode_utf8 in base/gp_utf8.c mishandles overlong UTF-8 encoding. NOTE: this issue exists because of an incomplete fix for CVE-2024-46954.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-46646
