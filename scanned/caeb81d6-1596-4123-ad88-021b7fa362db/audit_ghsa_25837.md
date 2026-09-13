# [C] Improper Restriction of XML External Entity Reference in Any23

## Summary
Severity: Critical
Advisory: GHSA-2rmm-87v7-34rj
CVE: CVE-2022-25312
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-06
Source: https://github.com/advisories/GHSA-2rmm-87v7-34rj
Type: github-advisory

## Affected
- Maven: `org.apache.any23:apache-any23` — affected >=0 <2.7

## Details
An XML external entity (XXE) injection vulnerability was discovered in the Any23 RDFa XSLTStylesheet extractor and is known to affect Any23 versions < 2.7. XML external entity injection (also known as XXE) is a web security vulnerability that allows an attacker to interfere with an application's processing of XML data. It often allows an attacker to view files on the application server filesystem, and to interact with any back-end or external systems that the application itself can access. This issue is fixed in Apache Any23 2.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25312
- https://github.com/apache/any23
- https://github.com/apache/any23/blob/any23-2.7/RELEASE-NOTES.md
- https://lists.apache.org/thread/y6cm5n3ksohsrhzqknqhzy7p3mtkyk23
- http://www.openwall.com/lists/oss-security/2022/03/04/2
