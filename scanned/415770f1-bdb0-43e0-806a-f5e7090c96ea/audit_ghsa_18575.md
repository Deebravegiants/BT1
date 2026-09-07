# [M] Apache JSPWiki Cross-Site Scripting (XSS) Vulnerability via Header Link Rendering

## Summary
Severity: Medium
Advisory: GHSA-rrff-chj9-w4c7
CVE: CVE-2025-24853
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-rrff-chj9-w4c7
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.12.3
- Maven: `org.apache.jspwiki:jspwiki-markdown` — affected >=0 <2.12.3

## Details
A carefully crafted request when creating a header link using the wiki markup syntax, which could allow the attacker to execute javascript in the victim's browser and get some sensitive information about the victim.

Further research by the JSPWiki team showed that the markdown parser allowed this kind of attack too.

Apache JSPWiki users should upgrade to 2.12.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24853
- https://github.com/apache/jspwiki/pull/376
- https://github.com/apache/jspwiki/commit/402f9a18b57dd910afba0139e6d3112d54ad650a
- https://github.com/apache/jspwiki/commit/f4089cb6d53223c2c291196ba687753a8b0422cf
- https://github.com/apache/jspwiki
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2025-24853
- http://www.openwall.com/lists/oss-security/2025/07/30/2
