# [M] Apache Struts directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wv7g-xhvw-8hcp
CVE: CVE-2008-6505
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wv7g-xhvw-8hcp
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.0.12
- Maven: `org.apache.struts:struts2-core` — affected >=2.1.0 <2.1.3

## Details
Multiple directory traversal vulnerabilities in Apache Struts 2.0.x before 2.0.12 and 2.1.x before 2.1.3 allow remote attackers to read arbitrary files via a `..%252f` (encoded dot dot slash) in a URI with a /struts/ path, related to (1) FilterDispatcher in 2.0.x and (2) DefaultStaticContentLoader in 2.1.x.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-6505
- https://github.com/apache/struts/commit/04fcefa44bae1263c7cad6986a9dafed67f0164f
- https://github.com/apache/struts/commit/1f1c996eb1f0f3e2193fba0075f62ccd04e3c0c3
- https://github.com/apache/struts
- https://web.archive.org/web/20081208214512/http://secunia.com/advisories/32497
- https://web.archive.org/web/20111025094319/http://www.securityfocus.com/bid/32104
- http://issues.apache.org/struts/browse/WW-2779
- http://struts.apache.org/2.x/docs/s2-004.html
