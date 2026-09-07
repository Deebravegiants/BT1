# [M] Jetty Uses Predictable Session Identifiers

## Summary
Severity: Medium
Advisory: GHSA-jg2x-r643-w2ch
CVE: CVE-2006-6969
CWE: CWE-330
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-jg2x-r643-w2ch
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=0 <4.2.27
- Maven: `org.eclipse.jetty:jetty-server` — affected >=5.1.0 <5.1.12
- Maven: `org.eclipse.jetty:jetty-server` — affected >=6.0.0 <6.0.2
- Maven: `org.eclipse.jetty:jetty-server` — affected >=6.1.0pre1 <6.1.0pre3

## Details
Jetty before 4.2.27, 5.1 before 5.1.12, 6.0 before 6.0.2, and 6.1 before 6.1.0pre3 generates predictable session identifiers using java.util.random, which makes it easier for remote attackers to guess a session identifier through brute force attacks, bypass authentication requirements, and possibly conduct cross-site request forgery attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-6969
- https://github.com/jetty-project/codehaus-jetty6/commit/36f81d2e7058b012f6718bc2f1e2786694a8a4a1
- https://github.com/jetty-project/codehaus-jetty6/commit/b31f606bf8058a38ab6253aa8dc2dfe6a7f83c78
- https://exchange.xforce.ibmcloud.com/vulnerabilities/32240
- https://github.com/jetty-project/codehaus-jetty6
- https://web.archive.org/web/20070208112816/http://fisheye.codehaus.org/changelog/jetty/?cs=1274
- https://web.archive.org/web/20070602184857/http://archives.neohapsis.com/archives/bugtraq/2007-02/0070.html
- https://web.archive.org/web/20121019131825/http://www.securityfocus.com/archive/1/459164/100/0/threaded
- https://web.archive.org/web/20200228100052/http://www.securityfocus.com/bid/22405
