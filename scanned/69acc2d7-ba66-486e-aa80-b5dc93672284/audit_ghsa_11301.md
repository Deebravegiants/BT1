# [M] Statamic has a path traversal in file dictionary fieldtype

## Summary
Severity: Medium
Advisory: GHSA-qm7r-wwq7-6f85
CVE: CVE-2026-33171
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-qm7r-wwq7-6f85
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.7.0
- Packagist: `statamic/cms` — affected >=0 <5.73.14

## Details
### Impact

Authenticated Control Panel users could read arbitrary `.json`, `.yaml`, and `.csv` files from the server by manipulating the file dictionary's `filename` configuration parameter in the fieldtype's endpoint.

### Patches

This has been fixed in 5.73.14 and 6.7.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-qm7r-wwq7-6f85
- https://nvd.nist.gov/vuln/detail/CVE-2026-33171
- https://github.com/statamic/cms
