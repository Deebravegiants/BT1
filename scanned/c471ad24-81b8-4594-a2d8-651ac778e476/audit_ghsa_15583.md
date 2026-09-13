# [H] Mautic vulnerable to Improper Access Control in UI upgrade process

## Summary
Severity: High
Advisory: GHSA-x3jx-5w6m-q2fc
CVE: CVE-2022-25768
CWE: CWE-284, CWE-287, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-x3jx-5w6m-q2fc
Type: github-advisory

## Affected
- Packagist: `mautic/core-lib` — affected >=1.1.3 <4.4.13
- Packagist: `mautic/core-lib` — affected >=5.0.0-alpha <5.1.1
- Packagist: `mautic/core` — affected >=1.1.3 <4.4.13
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.1.1

## Details
### Impact
The logic in place to facilitate the update process via the user interface lacks access control to verify if permission exists to perform the tasks. Prior to this patch being applied it might be possible for an attacker to access the Mautic version number or to execute parts of the upgrade process without permission. As upgrading in the user interface is deprecated, this functionality is no longer required.

### Patches
Upgrade to 4.4.13 or 5.1.1 or later.

### Workarounds
None.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-x3jx-5w6m-q2fc
- https://nvd.nist.gov/vuln/detail/CVE-2022-25768
- https://github.com/mautic/mautic/commit/89f964d06f00688016b38a56dfd9e95fc676c7ce
- https://github.com/mautic/mautic/commit/925aeee7d3dbb6ca67f92d9dc5893d99250f739b
- https://github.com/mautic/mautic
