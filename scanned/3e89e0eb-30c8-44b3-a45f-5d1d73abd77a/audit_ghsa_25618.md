# [M] Apache Tomcat allows webmasters to insert xss into error messages

## Summary
Severity: Medium
Advisory: GHSA-58hj-575g-5j25
CVE: CVE-2001-0829
CWE: CWE-80
Ecosystem: Maven
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-58hj-575g-5j25
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0

## Details
A cross-site scripting vulnerability in Apache Tomcat 3.2.1 allows a malicious webmaster to embed Javascript in a request for a .JSP file, which causes the Javascript to be inserted into an error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2001-0829
- https://web.archive.org/web/20021108153830/http://online.securityfocus.com/bid/2982
- https://web.archive.org/web/20021201182720/http://jakarta.apache.org/tomcat/tomcat-3.2-doc/readme
- https://web.archive.org/web/20061208015126/http://archive.cert.uni-stuttgart.de/archive/bugtraq/2001/07/msg00021.html
