# [M] Denial Of Service when opening a corrupt PDF file in pdfio

## Summary
Severity: Medium
Advisory: CVE-2023-24808
Aliases: GHSA-cjc4-x96x-fvgf
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-02-07
Source: https://osv.dev/vulnerability/CVE-2023-24808
Type: osv

## Details
PDFio is a C library for reading and writing PDF files. In versions prior to 1.1.0 a denial of service (DOS) vulnerability exists in the pdfio parser. Crafted pdf files can cause the program to run at 100% utilization and never terminate. The pdf which causes this crash found in testing is about 28kb in size and was discovered via fuzzing. Anyone who uses this library either as a standalone binary or as a library can be DOSed when attempting to parse this type of file. Web servers or other automated processes which rely on this code to turn pdf submissions into plaintext can be DOSed when an attacker uploads the pdf. Please see the linked GHSA for an example pdf. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24808.json
- https://github.com/michaelrsweet/pdfio/security/advisories/GHSA-cjc4-x96x-fvgf
- https://nvd.nist.gov/vuln/detail/CVE-2023-24808
- https://github.com/michaelrsweet/pdfio/commit/4f10021e7ee527c1aa24853e2947e38e154d9ccb
