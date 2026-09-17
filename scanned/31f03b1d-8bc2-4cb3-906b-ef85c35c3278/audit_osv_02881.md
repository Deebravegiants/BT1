# [H] ALPINE-CVE-2023-43115

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-43115
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-09-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-43115
Type: osv

## Affected
- Alpine:v3.18: `ghostscript` — affected >=0 <10.02.0-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <10.02.0-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <10.02.0-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <10.02.0-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <10.02.0-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <10.02.0-r0

## Details
In Artifex Ghostscript through 10.01.2, gdevijs.c in GhostPDL can lead to remote code execution via crafted PostScript documents because they can switch to the IJS device, or change the IjsServer parameter, after SAFER has been activated. NOTE: it is a documented risk that the IJS server can be specified on a gs command line (the IJS device inherently must execute a command to start the IJS server).

## References
- https://security.alpinelinux.org/vuln/CVE-2023-43115
