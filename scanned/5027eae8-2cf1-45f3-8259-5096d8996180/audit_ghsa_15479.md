# [M] Mautic has insufficient authentication in upgrade flow

## Summary
Severity: Medium
Advisory: GHSA-qf6m-6m4g-rmrc
CVE: CVE-2022-25770
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-qf6m-6m4g-rmrc
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=1.0.0-beta3 <4.4.13
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.1.1
- Packagist: `mautic/core-lib` — affected >=1.0.0-beta3 <4.4.13
- Packagist: `mautic/core-lib` — affected >=5.0.0-alpha <5.1.1

## Details
### Impact

Mautic allows you to update the application via an upgrade script.

The upgrade logic isn't shielded off correctly, which may lead to vulnerable situation.

This vulnerability is mitigated by the fact that Mautic needs to be installed in a certain way to be vulnerable

### Patches

Please upgrade to 4.4.1 or 5.1.1 or later.

### Workarounds
None.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-qf6m-6m4g-rmrc
- https://nvd.nist.gov/vuln/detail/CVE-2022-25770
- https://github.com/mautic/mautic/commit/73b18e9a434a28e528fe0e3d03620e7367bdcdca
- https://github.com/mautic/mautic/commit/aee7bfb7510a83acf178a7f02da9661c040e9abf
- https://github.com/mautic/mautic
