# [H] Moderate severity vulnerability that affects com.adobe.xmp:xmpcore

## Summary
Severity: High
Advisory: GHSA-qv32-7r6p-xhhh
CVE: CVE-2016-4216
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-qv32-7r6p-xhhh
Type: github-advisory

## Affected
- Maven: `com.adobe.xmp:xmpcore` — affected >=0 <5.1.3

## Details
XMPCore in Adobe XMP Toolkit for Java before 5.1.3 allows remote attackers to read arbitrary files via XML data containing an external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4216
- https://github.com/advisories/GHSA-qv32-7r6p-xhhh
- https://helpx.adobe.com/security/products/xmpcore/apsb16-24.html
- http://www.securityfocus.com/bid/91717
