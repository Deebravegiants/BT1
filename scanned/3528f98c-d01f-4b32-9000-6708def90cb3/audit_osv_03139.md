# [M] ALPINE-CVE-2024-50602

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-50602
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-50602
Type: osv

## Affected
- Alpine:v3.17: `expat` — affected >=0 <2.6.4-r0
- Alpine:v3.18: `expat` — affected >=0 <2.6.4-r0
- Alpine:v3.19: `expat` — affected >=0 <2.6.4-r0
- Alpine:v3.20: `expat` — affected >=0 <2.6.4-r0
- Alpine:v3.21: `expat` — affected >=0 <2.6.4-r0
- Alpine:v3.22: `expat` — affected >=0 <2.6.4-r0
- Alpine:v3.23: `expat` — affected >=0 <2.6.4-r0
- Alpine:v3.24: `expat` — affected >=0 <2.6.4-r0

## Details
An issue was discovered in libexpat before 2.6.4. There is a crash within the XML_ResumeParser function because XML_StopParser can stop/suspend an unstarted parser.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-50602
