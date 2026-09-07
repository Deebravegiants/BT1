# [M] Concrete CMS Stored XSS in Layout Preset Name

## Summary
Severity: Medium
Advisory: GHSA-x577-gcc9-9xjj
CVE: CVE-2023-48650
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-x577-gcc9-9xjj
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <8.5.14
- Packagist: `concrete5/concrete5` — affected >=9.0.0 <9.2.3

## Details
Concrete CMS before 8.5.14 and 9 before 9.2.3 is vulnerable to an admin adding a stored XSS payload via the Layout Preset name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48650
- https://github.com/concretecms/concretecms/commit/077755e6bbbc1c67b7508add9e3d207e8d8909a0
- https://github.com/concretecms/concretecms/commit/5b93470bcccf271810d3a0b190368ce6a9d6c84b
- https://documentation.concretecms.org/developers/introduction/version-history/923-release-notes
- https://github.com/concretecms/concretecms
- https://www.concretecms.org/about/project-news/security/2023-12-05-concrete-cms-new-cves-and-cve-updates
