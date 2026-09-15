# [M] CVE-2022-37050

## Summary
Severity: Medium
Advisory: CVE-2022-37050
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2022-37050
Type: osv

## Details
In Poppler 22.07.0, PDFDoc::savePageAs in PDFDoc.c callows attackers to cause a denial-of-service (application crashes with SIGABRT) by crafting a PDF file in which the xref data structure is mishandled in getCatalog processing. Note that this vulnerability is caused by the incomplete patch of CVE-2018-20662.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00037.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37050.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37050
- https://gitlab.freedesktop.org/poppler/poppler/-/issues/1274
- https://gitlab.freedesktop.org/poppler/poppler/-/commit/dcd5bd8238ea448addd102ff045badd0aca1b990
- https://lists.debian.org/debian-lts-announce/2023/10/msg00022.html
