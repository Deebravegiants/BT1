# [C] ALPINE-CVE-2025-27832

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-27832
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-27832
Type: osv

## Affected
- Alpine:v3.18: `ghostscript` — affected >=0 <10.05.0
- Alpine:v3.19: `ghostscript` — affected >=0 <10.05.0-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <10.05.0-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <10.05.0-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <10.05.0-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <10.05.0-r0

## Details
An issue was discovered in Artifex Ghostscript before 10.05.0. The NPDL device has a Compression buffer overflow for contrib/japanese/gdevnpdl.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-27832
