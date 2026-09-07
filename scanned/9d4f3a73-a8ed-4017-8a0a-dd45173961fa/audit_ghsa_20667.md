# [M] Apache JSPWiki XSS due to incomplete patch for CVE-2021-40369

## Summary
Severity: Medium
Advisory: GHSA-ggjq-8c4c-68r5
CVE: CVE-2022-28730
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-05
Source: https://github.com/advisories/GHSA-ggjq-8c4c-68r5
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.11.3

## Details
A carefully crafted request on AJAXPreview.jsp could trigger an XSS vulnerability on Apache JSPWiki, which could allow the attacker to execute javascript in the victim's browser and get some sensitive information about the victim. This vulnerability leverages CVE-2021-40369, where the Denounce plugin dangerously renders user-supplied URLs. Upon re-testing CVE-2021-40369, it appears that the patch was incomplete as it was still possible to insert malicious input via the Denounce plugin. Apache JSPWiki users should upgrade to 2.11.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28730
- https://github.com/apache/jspwiki
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2022-28732
