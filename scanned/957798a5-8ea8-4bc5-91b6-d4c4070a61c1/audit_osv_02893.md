# [H] ALPINE-CVE-2023-4504

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-4504
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-4504
Type: osv

## Affected
- Alpine:v3.17: `cups` — affected >=0 <2.4.7-r0
- Alpine:v3.18: `cups` — affected >=0 <2.4.7-r0
- Alpine:v3.19: `cups` — affected >=0 <2.4.7-r0
- Alpine:v3.20: `cups` — affected >=0 <2.4.7-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.7-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.7-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.7-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.7-r0

## Details
Due to failure in validating the length provided by an attacker-crafted PPD PostScript document, CUPS and libppd are susceptible to a heap-based buffer overflow and possibly code execution. This issue has been fixed in CUPS version 2.4.7, released in September of 2023.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-4504
