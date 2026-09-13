# [M] CSV Injection vulnerability with exported contact lists in Mautic

## Summary
Severity: Medium
Advisory: GHSA-29v9-2fpx-j5g9
CVE: CVE-2018-8092
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-01-19
Source: https://github.com/advisories/GHSA-29v9-2fpx-j5g9
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <2.13.0

## Details
### Impact
Mautic versions before 2.13.0 had a vulnerability that allowed a CSV injection with exported contact lists - https://www.owasp.org/index.php/CSV_Injection.

### Patches
Update to 2.13.0 or later.

### Workarounds
None.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-29v9-2fpx-j5g9
- https://nvd.nist.gov/vuln/detail/CVE-2018-8092
- https://github.com/mautic/mautic/commit/cbc49f0ac4cc7e3acc07f2a85c079b2f85225a6b
- https://github.com/mautic/mautic/releases/tag/2.13.0
