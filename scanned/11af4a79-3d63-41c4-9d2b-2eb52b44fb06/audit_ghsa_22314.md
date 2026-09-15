# [M] Jetty Directory Traversal Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qmgj-5h75-jr67
CVE: CVE-2006-2758
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-qmgj-5h75-jr67
Type: github-advisory

## Affected
- Maven: `org.mortbay.jetty:jetty` — affected >=0

## Details
Directory traversal vulnerability in jetty 6.0.x (jetty6) beta16 allows remote attackers to read arbitrary files via a `%2e%2e%5c` (encoded `../`) in the URL.  NOTE: this might be the same issue as CVE-2005-3747.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-2758
- https://github.com/jetty-project/codehaus-jetty6
- https://web.archive.org/web/20200302050157/http://securitytracker.com/id?1016168
