# [H] SQL injection in pimcore/pimcore

## Summary
Severity: High
Advisory: GHSA-g8jx-66p8-vcm2
CVE: CVE-2021-23405
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-07-13
Source: https://github.com/advisories/GHSA-g8jx-66p8-vcm2
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.0.7

## Details
This affects the package pimcore/pimcore before 10.0.7. This issue exists due to the absence of check on the storeId parameter in the method collectionsActionGet and groupsActionGet method within the ClassificationstoreController class.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23405
- https://github.com/pimcore/pimcore/pull/9572
- https://snyk.io/vuln/SNYK-PHP-PIMCOREPIMCORE-1316297
