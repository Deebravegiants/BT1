# [C] Command injection in itext7-core

## Summary
Severity: Critical
Advisory: GHSA-gv87-q66h-4277
CVE: CVE-2021-43113
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-gv87-q66h-4277
Type: github-advisory

## Affected
- Maven: `com.itextpdf:itext7-core` — affected >=0 <7.1.17
- Maven: `com.itextpdf:itextpdf` — affected >=0 <5.5.13.3

## Details
iTextPDF in iText before 7.1.17 allows command injection via a CompareTool filename that is mishandled on the gs (aka Ghostscript) command line in GhostscriptHelper.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43113
- https://github.com/itext/itext7
- https://github.com/itext/itext7/releases/tag/7.1.17
- https://github.com/itext/itextpdf/releases/tag/5.5.13.3
- https://lists.debian.org/debian-lts-announce/2023/01/msg00013.html
- https://pastebin.com/BXnkY9YY
- https://www.debian.org/security/2023/dsa-5323
