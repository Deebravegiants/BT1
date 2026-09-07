# [M] Out-of-bounds Read in iText

## Summary
Severity: Medium
Advisory: GHSA-8c9h-4q7g-fp7h
CVE: CVE-2022-24198
CWE: CWE-125
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-02
Source: https://github.com/advisories/GHSA-8c9h-4q7g-fp7h
Type: github-advisory

## Affected
- Maven: `com.itextpdf:itext7-core` — affected >=0 <7.2.0

## Details
iText v7.1.17 was discovered to contain an out-of-bounds exception via the component ARCFOUREncryption.encryptARCFOUR, which allows attackers to cause a Denial of Service (DoS) via a crafted PDF file. NOTE: Vendor does not view this as a vulnerability and has not found it to be exploitable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24198
- https://github.com/itext/itext7/pull/78
- https://github.com/itext/itext7/pull/78#issuecomment-1089287808
- https://github.com/itext/itext7
