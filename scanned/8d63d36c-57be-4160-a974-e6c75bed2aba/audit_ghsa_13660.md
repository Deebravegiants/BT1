# [H] Pimcore Admin UI has Two Factor Authentication disabled for non admin security firewalls

## Summary
Severity: High
Advisory: GHSA-9wwg-r3c7-4vfg
CVE: CVE-2023-49075
CWE: CWE-308
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-9wwg-r3c7-4vfg
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.2.2

## Details
### Impact
`AdminBundle\Security\PimcoreUserTwoFactorCondition` introduced in v11 disable the two factor authentication for all non-admin security firewalls.

An authenticated user can access the system without having to provide the 2 factor credentials.

### Patches
Apply patch https://patch-diff.githubusercontent.com/raw/pimcore/admin-ui-classic-bundle/pull/345.patch 

### Workarounds
Upgrade to version 1.2.2 or apply the [patch](https://patch-diff.githubusercontent.com/raw/pimcore/admin-ui-classic-bundle/pull/345.patch) manually.

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-9wwg-r3c7-4vfg
- https://nvd.nist.gov/vuln/detail/CVE-2023-49075
- https://github.com/pimcore/admin-ui-classic-bundle/pull/345
- https://github.com/pimcore/admin-ui-classic-bundle/commit/e412b0597830ae564a604e2579eb40e76f7f0628
- https://github.com/pimcore/admin-ui-classic-bundle
- https://patch-diff.githubusercontent.com/raw/pimcore/admin-ui-classic-bundle/pull/345.patch
