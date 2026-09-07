# [C] Pimcore Access Control Issues

## Summary
Severity: Critical
Advisory: GHSA-jhcf-j4hg-v64r
CVE: CVE-2019-18981
CWE: CWE-838
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jhcf-j4hg-v64r
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <6.2.2

## Details
Pimcore before 6.2.2 lacks an Access Denied outcome for a certain scenario of an incorrect recipient ID of a notification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18981
- https://github.com/pimcore/pimcore/commit/0a5d80b2593b2ebe35d19756b730ba33aa049106
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/compare/v6.2.1...v6.2.2
