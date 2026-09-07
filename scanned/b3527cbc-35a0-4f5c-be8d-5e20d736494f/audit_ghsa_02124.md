# [M] XSS vulnerability in theme config file in Mautic

## Summary
Severity: Medium
Advisory: GHSA-5w74-jx7m-x6hv
CVE: CVE-2018-8071
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-01-19
Source: https://github.com/advisories/GHSA-5w74-jx7m-x6hv
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <2.13.0

## Details
### Impact
Mautic before v2.13.0 has stored XSS via a theme config file.

### Patches
Update to 2.13.0 or later.

### Workarounds
None.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-5w74-jx7m-x6hv
- https://nvd.nist.gov/vuln/detail/CVE-2018-8071
- https://github.com/mautic/mautic/commit/3add236e9cc00ea9b211b52cccc4660379b2ee8b
- https://github.com/mautic/mautic/releases/tag/2.13.0
