# [M] Apache Tomcat has cookies without HTTPOnly flag in Set-Cookie header

## Summary
Severity: Medium
Advisory: GHSA-pvjh-7h8q-q56r
CVE: CVE-2010-4312
CWE: CWE-1004
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pvjh-7h8q-q56r
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.35

## Details
The default configuration of Apache Tomcat 6.x does not include the HTTPOnly flag in a Set-Cookie header, which makes it easier for remote attackers to hijack a session via script access to a cookie.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4312
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=608286
- https://github.com/apache/tomcat
- https://launchpad.net/bugs/cve/CVE-2010-4312
- https://security-tracker.debian.org/tracker/CVE-2010-4312
- https://ubuntu.com/security/CVE-2010-4312
