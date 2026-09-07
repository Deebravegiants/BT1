# [M] Mautic has an XSS in contact tracking and page hits report

## Summary
Severity: Medium
Advisory: GHSA-xpc5-rr39-v8v2
CVE: CVE-2021-27917
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-xpc5-rr39-v8v2
Type: github-advisory

## Affected
- Packagist: `mautic/core-lib` — affected >=1.0.0-beta4 <4.4.13
- Packagist: `mautic/core-lib` — affected >=5.0.0-alpha <5.1.1
- Packagist: `mautic/core` — affected >=1.0.0-beta4 <4.4.13
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.1.1

## Details
### Summary
Prior to this patch, a stored XSS vulnerability existed in the contact tracking and page hits report.

### Patches
Please update to 4.4.13 or 5.1.1 or later.

### Workarounds
None

### References
https://owasp.org/www-project-top-ten/2017/A7_2017-Cross-Site_Scripting_(XSS)
https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting

If you have any questions or comments about this advisory:

Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-xpc5-rr39-v8v2
- https://nvd.nist.gov/vuln/detail/CVE-2021-27917
- https://github.com/mautic/mautic/commit/550e33562d03363f7592fa9354259787a23a1d98
- https://github.com/mautic/mautic/commit/629165ac905c53bbb44feb5a6dbadb1dfd6d5564
- https://github.com/mautic/mautic
