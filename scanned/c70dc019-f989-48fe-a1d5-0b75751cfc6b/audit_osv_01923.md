# [H] ALPINE-CVE-2020-27778

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-27778
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-27778
Type: osv

## Affected
- Alpine:v3.12: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.13: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.14: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.15: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.16: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.17: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.18: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.19: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.20: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.21: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.22: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.23: `poppler` — affected >=0 <0.76.0-r0
- Alpine:v3.24: `poppler` — affected >=0 <0.76.0-r0

## Details
A flaw was found in Poppler in the way certain PDF files were converted into HTML. A remote attacker could exploit this flaw by providing a malicious PDF file that, when processed by the 'pdftohtml' program, would crash the application causing a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-27778
