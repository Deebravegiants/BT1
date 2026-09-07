# [M] XSS vulnerability in company name field in Mautic

## Summary
Severity: Medium
Advisory: GHSA-9hx7-rg7w-xm79
CVE: CVE-2018-11200
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-01-19
Source: https://github.com/advisories/GHSA-9hx7-rg7w-xm79
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <2.14.0

## Details
### Impact
Mautic version 2.11.0 and earlier contains a Cross Site Scripting (XSS) vulnerability in Company's name that can result in denial of service and execution of javascript code.

### Patches
Update to 2.14.0 or later.

### Workarounds
None.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-9hx7-rg7w-xm79
- https://nvd.nist.gov/vuln/detail/CVE-2018-11200
- https://github.com/mautic/mautic/releases/tag/2.14.0
