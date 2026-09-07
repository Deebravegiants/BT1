# [C] Variable Tampering within joomla/input class

## Summary
Severity: Critical
Advisory: GHSA-49fj-qp6p-q544
CVE: CVE-2022-23799
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-49fj-qp6p-q544
Type: github-advisory

## Affected
- Packagist: `joomla/input` — affected >=2.0.0 <2.0.2

## Details
An issue was discovered in Joomla! 4.0.0 through 4.1.0. Under specific circumstances, JInput pollutes method-specific input bags with $_REQUEST data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23799
- https://github.com/joomla/joomla-cms/issues/35541
- https://github.com/joomla-framework/input/commit/2086df5860a2edccd77c329ee7cbd118cfe93514
- https://developer.joomla.org/security-centre/876-20220307-core-variable-tampering-on-jinput-request-data.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/joomla/input/CVE-2022-23799.yaml
- https://github.com/joomla-framework/input
