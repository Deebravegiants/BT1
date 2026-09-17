# [H] ALPINE-CVE-2018-16802

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-16802
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16802
Type: osv

## Affected
- Alpine:v3.10: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.11: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.12: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.13: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.14: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.15: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.16: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.17: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.18: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.5: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.6: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.7: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.8: `ghostscript` — affected >=0 <9.25-r0
- Alpine:v3.9: `ghostscript` — affected >=0 <9.25-r0

## Details
An issue was discovered in Artifex Ghostscript before 9.25. Incorrect "restoration of privilege" checking when running out of stack during exception handling could be used by attackers able to supply crafted PostScript to execute code using the "pipe" instruction. This is due to an incomplete fix for CVE-2018-16509.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16802
