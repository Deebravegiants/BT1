# [C] Apache CXF Server-Side Request Forgery vulnerability

## Summary
Severity: Critical
Advisory: GHSA-x3x3-qwjq-8gj4
CVE: CVE-2022-46364
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-x3x3-qwjq-8gj4
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <3.4.10
- Maven: `org.apache.cxf:cxf-core` — affected >=3.5.0 <3.5.5

## Details
A SSRF vulnerability in parsing the href attribute of XOP:Include in MTOM requests in versions of Apache CXF before 3.5.5 and 3.4.10 allows an attacker to perform SSRF style attacks on webservices that take at least one parameter of any type.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46364
- https://cxf.apache.org/security-advisories.data/CVE-2022-46364.txt?version=1&modificationDate=1670944472739&api=v2
