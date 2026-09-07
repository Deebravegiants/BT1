# [M] Apache JSPWiki Cross-Site Scripting (XSS) Vulnerability in the Image Plugin

## Summary
Severity: Medium
Advisory: GHSA-72ww-4rcw-mc62
CVE: CVE-2025-24854
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-72ww-4rcw-mc62
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.12.3

## Details
A carefully crafted request using the Image plugin could trigger an XSS vulnerability on Apache JSPWiki, which could allow the attacker to execute javascript in the victim's browser and get some sensitive information about the victim.

Apache JSPWiki users should upgrade to 2.12.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24854
- https://github.com/apache/jspwiki
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2025-24854
- http://www.openwall.com/lists/oss-security/2025/07/30/3
