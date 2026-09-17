# [M] Predictable CSRF tokens in centreon/centreon

## Summary
Severity: Medium
Advisory: GHSA-7rg4-266c-jqw6
CVE: CVE-2021-28055
CWE: CWE-330, CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-7rg4-266c-jqw6
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=20.10.0 <20.10.7
- Packagist: `centreon/centreon` — affected >=20.04.0 <20.04.13
- Packagist: `centreon/centreon` — affected >=19.10.0 <19.10.23
- Packagist: `centreon/centreon` — affected >=0 <2.8.37

## Details
An issue was discovered in Centreon-Web in Centreon Platform 20.10.0. The anti-CSRF token generation is predictable, which might allow CSRF attacks that add an admin user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28055
- https://github.com/centreon/centreon/pull/9612
- https://github.com/centreon/centreon/commit/0261d4b250135eb513fdb7d52ba6fdeb19c6863f
- https://github.com/centreon/centreon/commit/626d3fb91cef402df0ebda5a8165d8f45da67c7a
- https://github.com/centreon/centreon
- https://github.com/centreon/centreon/releases/tag/19.10.23
- https://github.com/centreon/centreon/releases/tag/2.8.37
