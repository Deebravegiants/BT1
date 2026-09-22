# [M] ALPINE-CVE-2018-5686

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-5686
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5686
Type: osv

## Affected
- Alpine:v3.10: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.11: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.7: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.8: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.9: `mupdf` — affected >=0 <1.13-r0

## Details
In MuPDF 1.12.0, there is an infinite loop vulnerability and application hang in the pdf_parse_array function (pdf/pdf-parse.c) because EOF is not considered. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted pdf file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5686
