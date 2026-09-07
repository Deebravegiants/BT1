# [M] Cross-site Scriptin in JSPWiki

## Summary
Severity: Medium
Advisory: GHSA-hp5r-mhgp-56c9
CVE: CVE-2019-10078
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-06-06
Source: https://github.com/advisories/GHSA-hp5r-mhgp-56c9
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-war` — affected >=2.9.0 <2.11.0.M4
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=2.9.0 <2.11.0.M4

## Details
A carefully crafted plugin link invocation could trigger an XSS vulnerability on Apache JSPWiki 2.9.0 to 2.11.0.M3, which could lead to session hijacking. Initial reporting indicated ReferredPagesPlugin, but further analysis showed that multiple plugins were vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10078
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2019-10078
