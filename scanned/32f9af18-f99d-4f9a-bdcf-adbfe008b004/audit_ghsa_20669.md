# [M] Apache JSPWiki XSS due to crafted request in WeblogPlugin

## Summary
Severity: Medium
Advisory: GHSA-hph8-29xw-qfxx
CVE: CVE-2022-28732
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-05
Source: https://github.com/advisories/GHSA-hph8-29xw-qfxx
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.11.3

## Details
A carefully crafted request on WeblogPlugin could trigger an XSS vulnerability on Apache JSPWiki, which could allow the attacker to execute javascript in the victim's browser and get some sensitive information about the victim. Apache JSPWiki users should upgrade to 2.11.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28732
- https://github.com/apache/jspwiki
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2022-28732
