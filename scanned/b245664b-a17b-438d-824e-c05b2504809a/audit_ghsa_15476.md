# [M] Mautic vulnerable to XSS in contact/company tracking (no authentication)

## Summary
Severity: Medium
Advisory: GHSA-73gr-32wg-qhh7
CVE: CVE-2024-47050
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-73gr-32wg-qhh7
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=2.6.0 <4.4.13
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.1.1
- Packagist: `mautic/core-lib` — affected >=2.6.0 <4.4.13
- Packagist: `mautic/core-lib` — affected >=5.0.0-alpha <5.1.1

## Details
## Summary
Prior to this patch being applied, Mautic's tracking was vulnerable to Cross-Site Scripting through the Page URL variable.
  
## Patches
Please update to 4.4.13 or 5.1.1 or later.

## Workarounds
None

## References
https://owasp.org/www-project-top-ten/2017/A7_2017-Cross-Site_Scripting_(XSS)
https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting

If you have any questions or comments about this advisory:
Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-73gr-32wg-qhh7
- https://nvd.nist.gov/vuln/detail/CVE-2024-47050
- https://github.com/mautic/mautic/commit/0f21a3aa9c896788e1986fae0d7f166fc7a14c30
- https://github.com/mautic/mautic/commit/43db5e492c0ef82c917745849d5b454dbc8ca2c4
- https://github.com/mautic/mautic
