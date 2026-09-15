# [M] ALPINE-CVE-2024-33870

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-33870
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-33870
Type: osv

## Affected
- Alpine:v3.18: `ghostscript` — affected >=0 <10.04.0-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <10.03.1-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <10.03.1-r0

## Details
An issue was discovered in Artifex Ghostscript before 10.03.1. There is path traversal (via a crafted PostScript document) to arbitrary files if the current directory is in the permitted paths. For example, there can be a transformation of ../../foo to ./../../foo and this will grant access if ./ is permitted.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-33870
