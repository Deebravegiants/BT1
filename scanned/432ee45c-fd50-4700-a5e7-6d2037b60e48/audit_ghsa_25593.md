# [M] Jetty Javascript Inclusion Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5mq8-h82p-wjf2
CVE: CVE-2002-1533
CWE: CWE-80
Ecosystem: Maven
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-5mq8-h82p-wjf2
Type: github-advisory

## Affected
- Maven: `org.mortbay.jetty:jetty` — affected >=0 <4.1.1

## Details
Cross-site scripting (XSS) vulnerability in Jetty JSP servlet engine allows remote attackers to insert arbitrary HTML or script via an HTTP request to a .jsp file whose name contains the malicious script and some encoded linefeed characters (`%0a`).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2002-1533
- https://web.archive.org/web/20040705203137/http://xforce.iss.net/xforce/xfdb/10219
- https://web.archive.org/web/20041213153950/http://archives.neohapsis.com/archives/bugtraq/2002-09/0337.html
- https://web.archive.org/web/20061020173202/http://www.securityfocus.com/bid/5821
