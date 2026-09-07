# [M] Inline JS XSS vulnerability in Mautic

## Summary
Severity: Medium
Advisory: GHSA-qjhr-c23f-w76q
CVE: CVE-2017-1000488
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-01-19
Source: https://github.com/advisories/GHSA-qjhr-c23f-w76q
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=2.1.0 <2.12.0

## Details
### Impact

Mautic version 2.1.0 - 2.11.0 is vulnerable to an inline JS XSS attack when using Mautic forms on a Mautic landing page using GET parameters to pre-populate the form.

### Patches
Upgrade to 2.12.0 or later.

### Workarounds
None

### References
https://github.com/mautic/mautic/releases/tag/2.12.0

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-qjhr-c23f-w76q
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000488
- https://github.com/mautic/mautic/commit/bda60c0eefbd19c759589e975e63ab1d201c1b8e
- https://github.com/mautic/mautic/releases/tag/2.12.0
