# [M] Concrete CMS vulnerable to Improper Authentication

## Summary
Severity: Medium
Advisory: GHSA-q56r-mw39-944g
CVE: CVE-2022-43690
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-q56r-mw39-944g
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <8.5.10
- Packagist: `concrete5/concrete5` — affected >=9.0.0 <9.1.3

## Details
Concrete CMS (formerly concrete5) below 8.5.10 and between 9.0.0 and 9.1.2 did not use strict comparison for the legacy_salt so that limited authentication bypass could occur if using this functionality. Remediate by updating to Concrete CMS 9.1.3+ or 8.5.10+.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43690
- https://github.com/concretecms/concretecms/commit/a4dc73a4a47823373d4b4824534bb9b7d251f72c
- https://github.com/concretecms/concretecms/commit/d5dd12c40efed326b26862391b7e1e6f414cdd55
- https://documentation.concretecms.org/developers/introduction/version-history/8510-release-notes
- https://documentation.concretecms.org/developers/introduction/version-history/913-release-notes
- https://github.com/concretecms/concretecms
- https://github.com/concretecms/concretecms/releases/8.5.10
- https://github.com/concretecms/concretecms/releases/9.1.3
- https://www.concretecms.org/about/project-news/security/concrete-cms-security-advisory-2022-10-31
