# [M] Mautic vulnerable to Cross-site Scripting (XSS) - stored (edit form HTML field)

## Summary
Severity: Medium
Advisory: GHSA-xv68-rrmw-9xwf
CVE: CVE-2024-47058
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-xv68-rrmw-9xwf
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.1.1
- Packagist: `mautic/core` — affected >=1.0.0-beta <4.4.13
- Packagist: `mautic/core-lib` — affected >=5.0.0-alpha <5.1.1
- Packagist: `mautic/core-lib` — affected >=1.0.0-beta <4.4.13

## Details
### Impact
With access to edit a Mautic form, the attacker can add Cross-Site Scripting stored in the html filed. This could be used to steal sensitive information from the user's current session.

### Patches
Upgrade to 4.4.13 or 5.1.1 or later.

### Workarounds
None

### References
- https://owasp.org/www-project-top-ten/2017/A7_2017-Cross-Site_Scripting_(XSS)
- https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting

If you have any questions or comments about this advisory:

Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-xv68-rrmw-9xwf
- https://nvd.nist.gov/vuln/detail/CVE-2024-47058
- https://github.com/mautic/mautic/commit/344b908ef690283e7d8d3fc5cc1327396a1c3046
- https://github.com/mautic/mautic/commit/88153a15b3cea331b7036d956b880c69e81a0032
- https://github.com/mautic/mautic
