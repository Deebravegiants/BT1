# [H] Disabled users able to log in with third party SSO plugin

## Summary
Severity: High
Advisory: GHSA-6x98-fx9j-7c78
CVE: CVE-2017-1000489
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-01-19
Source: https://github.com/advisories/GHSA-6x98-fx9j-7c78
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=2.0.0 <2.12.0

## Details
### Impact
Mautic versions 2.0.0 - 2.11.0 with a SSO plugin installed could allow a disabled user to still login using email address

### Patches
Upgrade to 2.12.0 or later.

### Workarounds
None.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-6x98-fx9j-7c78
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000489
- https://github.com/mautic/mautic/commit/fd933cbef795b04cabdc50527cb18e037488fef9
- https://github.com/mautic/mautic/releases/tag/2.12.0
