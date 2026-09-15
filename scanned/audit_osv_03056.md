# [H] ALPINE-CVE-2024-34459

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-34459
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-34459
Type: osv

## Affected
- Alpine:v3.18: `libxml2` — affected >=2.12.0 <2.11.8-r0
- Alpine:v3.19: `libxml2` — affected >=2.12.0 <2.11.8-r0
- Alpine:v3.20: `libxml2` — affected >=2.12.0 <2.12.7-r0
- Alpine:v3.21: `libxml2` — affected >=2.12.0 <2.12.7-r0
- Alpine:v3.22: `libxml2` — affected >=2.12.0 <2.12.7-r0
- Alpine:v3.23: `libxml2` — affected >=2.12.0 <2.12.7-r0
- Alpine:v3.24: `libxml2` — affected >=2.12.0 <2.12.7-r0

## Details
An issue was discovered in xmllint (from libxml2) before 2.11.8 and 2.12.x before 2.12.7. Formatting error messages with xmllint --htmlout can result in a buffer over-read in xmlHTMLPrintFileContext in xmllint.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-34459
