# [M] Bypass of fix for CVE-2020-26231, Twig sandbox escape

## Summary
Severity: Medium
Advisory: GHSA-fcr8-6q7r-m4wg
CVE: CVE-2021-21264
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2021-05-04
Source: https://github.com/advisories/GHSA-fcr8-6q7r-m4wg
Type: github-advisory

## Affected
- Packagist: `october/cms` — affected >=1.0.471 <1.0.472
- Packagist: `october/cms` — affected >=1.1.1 <1.1.2

## Details
### Impact
A bypass of CVE-2020-26231 (fixed in 1.0.470/471 and 1.1.1) was discovered that has the same impact as CVE-2020-26231 & CVE-2020-15247:

An authenticated backend user with the `cms.manage_pages`, `cms.manage_layouts`, or `cms.manage_partials` permissions who would **normally** not be permitted to provide PHP code to be executed by the CMS due to `cms.enableSafeMode` being enabled is able to write specific Twig code to escape the Twig sandbox and execute arbitrary PHP.

This is not a problem for anyone that trusts their users with those permissions to normally write & manage PHP within the CMS by not having `cms.enableSafeMode` enabled, but would be a problem for anyone relying on `cms.enableSafeMode` to ensure that users with those permissions in production do not have access to write & execute arbitrary PHP.

### Patches
Issue has been patched in Build 472 (v1.0.472) and v1.1.2.

### Workarounds
Apply https://github.com/octobercms/october/commit/f63519ff1e8d375df30deba63156a2fc97aa9ee7 to your installation manually if unable to upgrade to Build 472 or v1.1.2.

### References
Reported by [ka1n4t](https://github.com/ka1n4t)

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

### Threat assessment:
<img width="1108" alt="Screen Shot 2020-10-10 at 1 21 13 PM" src="https://user-images.githubusercontent.com/7253840/95663316-7de28b80-0afb-11eb-999d-a6526cf78709.png">

## References
- https://github.com/octobercms/october/security/advisories/GHSA-fcr8-6q7r-m4wg
- https://nvd.nist.gov/vuln/detail/CVE-2021-21264
- https://github.com/octobercms/october
