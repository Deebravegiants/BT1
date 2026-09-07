# [M] Apache JSPWiki CSRF due to crafted request on UserPreferences.jsp

## Summary
Severity: Medium
Advisory: GHSA-9x9j-vrhj-v364
CVE: CVE-2022-28731
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-08-05
Source: https://github.com/advisories/GHSA-9x9j-vrhj-v364
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.11.3

## Details
A carefully crafted request on UserPreferences.jsp could trigger an CSRF vulnerability on Apache JSPWiki before 2.11.3, which could allow the attacker to modify the email associated with the attacked account, and then a reset password request from the login page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28731
- https://github.com/apache/jspwiki
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2022-28732
