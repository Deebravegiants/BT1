# [M] Symbiote Seed Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wm32-3r4m-jvcc
CVE: CVE-2017-20164
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-07
Source: https://github.com/advisories/GHSA-wm32-3r4m-jvcc
Type: github-advisory

## Affected
- Packagist: `symbiote/silverstripe-seed` — affected >=0 <6.0.3

## Details
A vulnerability was found in Symbiote Seed up to 6.0.2. It has been classified as critical. Affected is the function `onBeforeSecurityLogin` of the file `code/extensions/SecurityLoginExtension.php` of the component `Login`. The manipulation of the argument URL leads to open redirect. It is possible to launch the attack remotely. Upgrading to version 6.0.3 can address this issue. The name of the patch is b065ebd82da53009d273aa7e989191f701485244. It is recommended to upgrade the affected component. VDB-217626 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20164
- https://github.com/symbiote/silverstripe-seed/commit/b065ebd82da53009d273aa7e989191f701485244
- https://github.com/symbiote/silverstripe-seed
- https://github.com/symbiote/silverstripe-seed/releases/tag/6.0.3
