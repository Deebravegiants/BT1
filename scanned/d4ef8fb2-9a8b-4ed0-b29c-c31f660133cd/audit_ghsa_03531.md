# [M] Path Traversal within joomla/archive zip class

## Summary
Severity: Medium
Advisory: GHSA-vgwr-773q-7j3c
CVE: CVE-2021-26028
CWE: CWE-22
Ecosystem: Packagist
Published: 2021-03-24
Source: https://github.com/advisories/GHSA-vgwr-773q-7j3c
Type: github-advisory

## Affected
- Packagist: `joomla/archive` — affected >=0 <1.1.10

## Details
An issue was discovered in Joomla! 3.0.0 through 3.9.24. Extracting an specifilcy crafted zip package could write files outside of the intended path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26028
- https://github.com/joomla-framework/archive/commit/32c9009a1020d16bc1060c0d06339898b697cf2c
- https://developer.joomla.org/security-centre/848-20210308-core-path-traversal-within-joomla-archive-zip-class.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/joomla/archive/CVE-2021-26028.yaml
