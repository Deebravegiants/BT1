# [M] Cross-site Scripting (XSS) in Conditions tab of Pricing Rules

## Summary
Severity: Medium
Advisory: GHSA-r7mm-jx6h-hv7m
CVE: CVE-2023-2332
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-r7mm-jx6h-hv7m
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.


### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/a4491551967d879141a3fdf0986a9dd3d891abfe.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/a4491551967d879141a3fdf0986a9dd3d891abfe.patch manually.

### References
https://huntr.dev/bounties/e436ed71-6741-4b30-89db-f7f3de4aca2c/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-r7mm-jx6h-hv7m
- https://nvd.nist.gov/vuln/detail/CVE-2023-2332
- https://github.com/pimcore/pimcore/commit/a4491551967d879141a3fdf0986a9dd3d891abfe
- https://github.com/pimcore/pimcore
- https://huntr.com/bounties/e436ed71-6741-4b30-89db-f7f3de4aca2c
