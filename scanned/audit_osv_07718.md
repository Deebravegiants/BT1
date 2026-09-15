# [H] Apache Tomcat: Security constraint bypass for CGI scripts

## Summary
Severity: High
Advisory: BIT-tomcat-2025-46701
Aliases: CVE-2025-46701, GHSA-h2fw-rfh5-95r3
Ecosystem: Bitnami
Published: 2025-07-10
Source: https://osv.dev/vulnerability/BIT-tomcat-2025-46701
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.7

## Details
Improper Handling of Case Sensitivity vulnerability in Apache Tomcat's GCI servlet allows security constraint bypass of security constraints that apply to the pathInfo component of a URI mapped to the CGI servlet.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.6, from 10.1.0 through 10.1.40, from 9.0.0 through 9.0.104.
The following versions were EOL at the time the CVE was created but are 
known to be affected: 8.5.0 though 8.5.100. Other, older, EOL versions 
may also be affected.


Users are recommended to upgrade to version 11.0.7, 10.1.41 or 9.0.105, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/05/29/4
- https://lists.apache.org/thread/xhqqk9w5q45srcdqhogdk04lhdscv30j
- https://nvd.nist.gov/vuln/detail/CVE-2025-46701
- https://lists.debian.org/debian-lts-announce/2025/07/msg00009.html
