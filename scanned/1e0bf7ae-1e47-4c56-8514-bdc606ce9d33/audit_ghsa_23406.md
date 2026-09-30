# [H] Improper input validation in Mort Bay Jetty

## Summary
Severity: High
Advisory: GHSA-6jxp-7g74-2rc3
CVE: CVE-2009-4611
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-6jxp-7g74-2rc3
Type: github-advisory

## Affected
- Maven: `org.mortbay.jetty:jetty` — affected >=6.0.0 <6.1.23
- Maven: `org.mortbay.jetty:jetty` — affected >=7.0.0 <7.0.2

## Details
Mort Bay Jetty 6.x through 6.1.22 and 7.0.0 writes backtrace data without sanitizing non-printable characters, which might allow remote attackers to modify a window's title, or possibly execute arbitrary commands or overwrite files, via an HTTP request containing an escape sequence for a terminal emulator, related to (1) a string value in the Age parameter to the default URI for the Cookie Dump Servlet in test-jetty-webapp/src/main/java/com/acme/CookieDump.java under cookie/, (2) an alphabetic value in the A parameter to jsp/expr.jsp, or (3) an alphabetic value in the Content-Length HTTP header to an arbitrary application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-4611
- https://fossies.org/linux/jetty-distribution/VERSION.txt
- https://github.com/eclipse/jetty.project
- https://www.eclipse.org/jetty/about.php
- http://www.ush.it/team/ush/hack-jetty6x7x/jetty-adv.txt
- http://www.ush.it/team/ush/hack_httpd_escape/adv.txt
