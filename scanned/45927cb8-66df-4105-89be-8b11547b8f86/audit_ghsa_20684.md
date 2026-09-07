# [H] Apache JSPWiki CSRF due to crafted invocation on the Image plugin

## Summary
Severity: High
Advisory: GHSA-jp3m-p26h-mm7v
CVE: CVE-2022-34158
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-05
Source: https://github.com/advisories/GHSA-jp3m-p26h-mm7v
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.11.3

## Details
A carefully crafted invocation on the Image plugin could trigger an CSRF vulnerability on Apache JSPWiki before 2.11.3, which could allow a group privilege escalation of the attacker's account. Further examination of this issue established that it could also be used to modify the email associated with the attacked account, and then a reset password request from the login page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34158
- https://github.com/apache/jspwiki
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2022-34158
