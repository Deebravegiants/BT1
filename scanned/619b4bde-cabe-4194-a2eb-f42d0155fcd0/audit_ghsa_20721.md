# [M] Apache JSPWiki XSS due to crafted request on XHRHtml2Markup.jsp

## Summary
Severity: Medium
Advisory: GHSA-2fxf-qj94-3f83
CVE: CVE-2022-27166
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-05
Source: https://github.com/advisories/GHSA-2fxf-qj94-3f83
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.11.3

## Details
A carefully crafted request on XHRHtml2Markup.jsp could trigger an XSS vulnerability on Apache JSPWiki up to and including 2.11.2, which could allow the attacker to execute javascript in the victim's browser and get some sensitive information about the victim. Version 2.11.3 contains a fix for the problem

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27166
- https://github.com/apache/jspwiki
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2022-28732
