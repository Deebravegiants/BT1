# [M] Apache Tomcat's CookieExample Vulnerable to XSS

## Summary
Severity: Medium
Advisory: GHSA-36hp-4x3g-phrg
CVE: CVE-2007-3384
CWE: CWE-80
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-36hp-4x3g-phrg
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=3.3.0

## Details
Multiple cross-site scripting (XSS) vulnerabilities in `examples/servlet/CookieExample` in Apache Tomcat 3.3 through 3.3.2 allow remote attackers to inject arbitrary web script or HTML via the (1) Name or (2) Value field, related to error messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-3384
- https://web.archive.org/web/20070824135030/http://securityreason.com/securityalert/2971
- https://web.archive.org/web/20071117100258/http://securitytracker.com/alerts/2007/Aug/1018503.html
- https://web.archive.org/web/20170323011513/http://www.securityfocus.com/bid/25174
- https://web.archive.org/web/20201207035111/http://www.securityfocus.com/archive/1/475321/100/0/threaded
- http://tomcat.apache.org/security-3.html
