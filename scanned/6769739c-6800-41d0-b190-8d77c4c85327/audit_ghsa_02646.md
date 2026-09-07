# [C] XML Injection in Any23

## Summary
Severity: Critical
Advisory: GHSA-838r-hvwh-24h8
CVE: CVE-2021-38555
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-09-13
Source: https://github.com/advisories/GHSA-838r-hvwh-24h8
Type: github-advisory

## Affected
- Maven: `org.apache.any23:apache-any23` — affected >=0 <2.5

## Details
An XML external entity (XXE) injection vulnerability was discovered in the Any23 StreamUtils.java file and is known to affect Any23 versions < 2.5. XML external entity injection (also known as XXE) is a web security vulnerability that allows an attacker to interfere with an application's processing of XML data. It often allows an attacker to view files on the application server filesystem, and to interact with any back-end or external systems that the application itself can access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38555
- https://github.com/apache/any23
- https://lists.apache.org/thread.html/r589d1a9f94dbeee7a0f5dbe8513a0e300dfe669bd964ba2fbfe28e07%40%3Cannounce.apache.org%3E
