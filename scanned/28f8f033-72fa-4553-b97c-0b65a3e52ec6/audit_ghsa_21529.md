# [M] Concrete CMS vulnerable to Uncontrolled Resource Consumption leading to DoS

## Summary
Severity: Medium
Advisory: GHSA-3cxx-3f53-m92c
CVE: CVE-2022-43686
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-3cxx-3f53-m92c
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <8.5.10
- Packagist: `concrete5/concrete5` — affected >=9.0.0 <9.1.3

## Details
In Concrete CMS (formerly concrete5) below 8.5.10 and between 9.0.0 and 9.1.2, the authTypeConcreteCookieMap table can be filled up causing a denial of service (high load).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43686
- https://documentation.concretecms.org/developers/introduction/version-history/8510-release-notes
- https://documentation.concretecms.org/developers/introduction/version-history/913-release-notes
- https://github.com/concretecms/concretecms
- https://github.com/concretecms/concretecms/releases/8.5.10
- https://github.com/concretecms/concretecms/releases/9.1.3
- https://www.concretecms.org/about/project-news/security/concrete-cms-security-advisory-2022-10-31
