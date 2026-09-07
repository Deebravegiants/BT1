# [H] XSS vulnerability on asset view

## Summary
Severity: High
Advisory: GHSA-rh5w-82wh-jhr8
CVE: CVE-2021-27912
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-rh5w-82wh-jhr8
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <3.3.4
- Packagist: `mautic/core` — affected >=4.0.0-alpha1 <4.0.0

## Details
### Impact
Mautic versions before 3.3.4 / 4.0.0 are vulnerable to an inline JS XSS attack when viewing Mautic assets by utilizing inline JS in the title and adding a broken image URL as a remote asset. This can only be leveraged by an authenticated user with permission to create or edit assets. 

### Patches
Upgrade to 3.3.4 or 4.0.0

### Workarounds
No

### References
https://github.com/mautic/mautic/releases/tag/3.3.4
https://github.com/mautic/mautic/releases/tag/4.0.0

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-rh5w-82wh-jhr8
- https://nvd.nist.gov/vuln/detail/CVE-2021-27912
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mautic/core/CVE-2021-27912.yaml
- https://github.com/mautic/mautic
