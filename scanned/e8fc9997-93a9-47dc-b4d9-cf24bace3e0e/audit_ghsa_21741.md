# [C] Possible SQL injection in tablelookupwizard Contao Extension

## Summary
Severity: Critical
Advisory: GHSA-v3mr-gp7j-pw5w
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-v3mr-gp7j-pw5w
Type: github-advisory

## Affected
- Packagist: `terminal42/contao-tablelookupwizard` — affected >=0 <3.3.5

## Details
### Impact
The currently selected widget values were not correctly sanitized before passing it to the database, leading to an SQL injection possibility.

### Patches
The issue has been patched in `tablelookupwizard` version 3.3.5 and version 4.0.0.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/terminal42/contao-tablelookupwizard
* Email us at [info@terminal42.ch](mailto:info@terminal42.ch)

## References
- https://github.com/terminal42/contao-tablelookupwizard/security/advisories/GHSA-v3mr-gp7j-pw5w
- https://github.com/terminal42/contao-tablelookupwizard/commit/a5e723a28f110b7df8ffc4175cef9b061d3cc717
- https://github.com/FriendsOfPHP/security-advisories/blob/master/terminal42/contao-tablelookupwizard/2022-02-04-1.yaml
- https://github.com/terminal42/contao-tablelookupwizard
