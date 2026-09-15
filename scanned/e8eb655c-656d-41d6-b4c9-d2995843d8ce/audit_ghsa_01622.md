# [M] Twig Sandbox Escape by authenticated users with access to editing CMS templates when safemode is enabled.

## Summary
Severity: Medium
Advisory: GHSA-94vp-rmqv-5875
CVE: CVE-2020-15247
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2020-11-23
Source: https://github.com/advisories/GHSA-94vp-rmqv-5875
Type: github-advisory

## Affected
- Packagist: `october/cms` — affected >=1.0.319 <1.0.469

## Details
### Impact
An authenticated backend user with the `cms.manage_pages`, `cms.manage_layouts`, or `cms.manage_partials` permissions who would **normally** not be permitted to provide PHP code to be executed by the CMS due to `cms.enableSafeMode` being enabled is able to write specific Twig code to escape the Twig sandbox and execute arbitrary PHP.

This is not a problem for anyone that trusts their users with those permissions to normally write & manage PHP within the CMS by not having `cms.enableSafeMode` enabled, but would be a problem for anyone relying on `cms.enableSafeMode` to ensure that users with those permissions in production do not have access to write & execute arbitrary PHP.

### Patches
Issue has been patched in Build 469 (v1.0.469) and v1.1.0.

### Workarounds
Apply https://github.com/octobercms/october/compare/106daa2930de4cebb18732732d47d4056f01dd5b...7cb148c1677373ac30ccfd3069d18098e403e1ca to your installation manually if unable to upgrade to Build 469.

### References
Reported by [ka1n4t](https://github.com/ka1n4t)

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

### Threat assessment:
<img width="1108" alt="Screen Shot 2020-10-10 at 1 21 13 PM" src="https://user-images.githubusercontent.com/7253840/95663316-7de28b80-0afb-11eb-999d-a6526cf78709.png">

## References
- https://github.com/octobercms/october/security/advisories/GHSA-94vp-rmqv-5875
- https://nvd.nist.gov/vuln/detail/CVE-2020-15247
- https://github.com/octobercms/october/commit/4c650bb775ab849e48202a4923bac93bd74f9982
- https://github.com/octobercms/october
