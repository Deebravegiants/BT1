# [M] Out-of-bounds Write in iText

## Summary
Severity: Medium
Advisory: GHSA-c32g-2mgr-cfq7
CVE: CVE-2022-24197
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-02
Source: https://github.com/advisories/GHSA-c32g-2mgr-cfq7
Type: github-advisory

## Affected
- Maven: `com.itextpdf:itext7-core` — affected >=0 <7.1.18

## Details
iText v7.1.17 was discovered to contain a stack-based buffer overflow via the component ByteBuffer.append, which allows attackers to cause a Denial of Service (DoS) via a crafted PDF file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24197
- https://github.com/itext/itext7/pull/78
- https://github.com/itext/itext7/pull/78#issuecomment-1089282165
- https://github.com/itext/itext7
- https://github.com/itext/itext7/releases/tag/7.1.18
