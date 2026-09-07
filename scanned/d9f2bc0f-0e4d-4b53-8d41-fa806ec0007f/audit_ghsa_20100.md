# [M] Concrete CMS vulnerable to cross-site scripting in the text input field

## Summary
Severity: Medium
Advisory: GHSA-xj33-8r43-r227
CVE: CVE-2022-43556
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-06
Source: https://github.com/advisories/GHSA-xj33-8r43-r227
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <8.5.10
- Packagist: `concrete5/concrete5` — affected >=9.0.0 <9.1.3

## Details
Concrete CMS (formerly concrete5) below 8.5.10 and between 9.0.0 and 9.1.2 is vulnerable to XSS in the text input field since the result dashboard page output is not sanitized. The Concrete CMS security team has ranked this 4.2 with CVSS v3.1 vector AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N Remediate by updating to Concrete CMS 8.5.10 and Concrete CMS 9.1.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43556
- https://documentation.concretecms.org/developers/introduction/version-history/8510-release-notes
- https://documentation.concretecms.org/developers/introduction/version-history/913-release-notes
- https://github.com/concretecms/concretecms
- https://www.concretecms.org/about/project-news/security/concrete-cms-security-advisory-2022-10-31
