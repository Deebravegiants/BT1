# [H] ALPINE-CVE-2024-33871

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-33871
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-33871
Type: osv

## Affected
- Alpine:v3.18: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <10.03.1-r0

## Details
An issue was discovered in Artifex Ghostscript before 10.03.1. contrib/opvp/gdevopvp.c allows arbitrary code execution via a custom Driver library, exploitable via a crafted PostScript document. This occurs because the Driver parameter for opvp (and oprp) devices can have an arbitrary name for a dynamic library; this library is then loaded.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-33871
