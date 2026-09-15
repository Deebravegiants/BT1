# [M] Mortbay Jetty Double Slash URI Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4jjw-xrr6-9v3p
CVE: CVE-2007-6672
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-4jjw-xrr6-9v3p
Type: github-advisory

## Affected
- Maven: `org.mortbay.jetty:jetty` — affected >=6.1.5 <6.1.7

## Details
Mortbay Jetty 6.1.5 and 6.1.6 allows remote attackers to bypass protection mechanisms and read the source of files via multiple `/` (slash) characters in the URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6672
- https://web.archive.org/web/20080113051254/http://www.kb.cert.org/vuls/id/553235
- https://web.archive.org/web/20080120225723/http://jira.codehaus.org/browse/JETTY-386
- https://web.archive.org/web/20080120225728/http://jira.codehaus.org/browse/JETTY/fixforversion/13950
- https://web.archive.org/web/20080517012615/http://www.securityfocus.com/bid/27117
