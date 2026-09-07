# [M] XSS vulnerability on password reset page

## Summary
Severity: Medium
Advisory: GHSA-32hw-3pvh-vcvc
CVE: CVE-2021-27909
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-32hw-3pvh-vcvc
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <3.3.4
- Packagist: `mautic/core` — affected >=4.0.0-alpha1 <4.0.0

## Details
### Impact
For Mautic versions prior to 3.3.4, there is an XSS vulnerability on Mautic's password reset page where a vulnerable parameter, "bundle," in the URL could allow an attacker to execute Javascript code. The attacker would be required to convince or trick the target into clicking a password reset URL with the vulnerable parameter utilized. 

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
- https://github.com/mautic/mautic/security/advisories/GHSA-32hw-3pvh-vcvc
- https://nvd.nist.gov/vuln/detail/CVE-2021-27909
- https://github.com/mautic/mautic/commit/942cb6992df619fdf1c181bfad9e25d5d4178b6f
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mautic/core/CVE-2021-27909.yaml
- https://github.com/mautic/mautic
