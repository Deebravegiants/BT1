# [M] ConcreteCMS Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p4jj-gwpg-9jwh
CVE: CVE-2023-44761
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-06
Source: https://github.com/advisories/GHSA-p4jj-gwpg-9jwh
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.2.2

## Details
Multiple Cross Site Scripting (XSS) vulnerabilities in Concrete CMS v.9.2.1 allow a local attacker to execute arbitrary code via a crafted script to the Forms of the Data objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44761
- https://github.com/concretecms/concretecms
- https://github.com/sromanhu/ConcreteCMS-Stored-XSS---Forms
- https://www.concretecms.org/about/project-news/security/2023-11-09-security-blog-about-updated-cves-and-new-release
