# [M] Apache JSPWiki Cross-site Scripting due to carefully crafted plugin link invocation

## Summary
Severity: Medium
Advisory: GHSA-cfqj-9g2g-w7q6
CVE: CVE-2021-40369
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-02
Source: https://github.com/advisories/GHSA-cfqj-9g2g-w7q6
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.11.0

## Details
A carefully crafted plugin link invocation could trigger an XSS vulnerability on Apache JSPWiki, related to the Denounce plugin, which could allow the attacker to execute javascript in the victim's browser and get some sensitive information about the victim. Apache JSPWiki users should upgrade to 2.11.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40369
- https://github.com/apache/jspwiki
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2021-40369
- https://lists.apache.org/thread/r2j00nrnpjgcmoxvlv3pgfoq9kzrcsfh
- http://www.openwall.com/lists/oss-security/2022/08/03/3
