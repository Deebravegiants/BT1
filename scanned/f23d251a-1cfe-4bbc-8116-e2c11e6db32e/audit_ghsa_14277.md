# [M] Cross-site Scripting (XSS) in DataObjects QuantityValue Unit Definition

## Summary
Severity: Medium
Advisory: GHSA-2295-vh28-pphc
CVE: CVE-2023-2328
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-2295-vh28-pphc
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.21 or apply these patches manually https://github.com/pimcore/pimcore/commit/e3562bfe249c557d15474c9a0acd5e06628521fe.patch
https://github.com/pimcore/pimcore/commit/b9c9ca2371aa643dbc4caca162ff3400266ff96f.patch

### Workarounds
Apply patches:
https://github.com/pimcore/pimcore/commit/e3562bfe249c557d15474c9a0acd5e06628521fe.patch
https://github.com/pimcore/pimcore/commit/b9c9ca2371aa643dbc4caca162ff3400266ff96f.patch

### References
https://huntr.dev/bounties/01a44584-e36b-46f4-ad94-53af488397f6/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-2295-vh28-pphc
- https://nvd.nist.gov/vuln/detail/CVE-2023-2328
- https://github.com/pimcore/pimcore/commit/e3562bfe249c557d15474c9a0acd5e06628521fe
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/01a44584-e36b-46f4-ad94-53af488397f6
