# [M] ALPINE-CVE-2024-29510

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-29510
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-29510
Type: osv

## Affected
- Alpine:v3.18: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <10.03.1-r0

## Details
Artifex Ghostscript before 10.03.1 allows memory corruption, and SAFER sandbox bypass, via format string injection with a uniprint device.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-29510
