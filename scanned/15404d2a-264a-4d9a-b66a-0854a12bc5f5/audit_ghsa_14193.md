# [M] Cross-site Scripting (XSS) in DataObject Any Getter grid operator

## Summary
Severity: Medium
Advisory: GHSA-6fvf-x8c6-2f6j
CVE: CVE-2023-2339
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-6fvf-x8c6-2f6j
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
Stored cross site scripting vulnerability in operator any getter in dataobject grid configuration.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/6946f8a5a0a93b516c49f17a5b45044eebd73480.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/6946f8a5a0a93b516c49f17a5b45044eebd73480.patch manually.

### References
https://huntr.dev/bounties/bb1537a5-fe7b-4c77-a582-10a82435fbc2/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-6fvf-x8c6-2f6j
- https://nvd.nist.gov/vuln/detail/CVE-2023-2339
- https://github.com/pimcore/pimcore/commit/6946f8a5a0a93b516c49f17a5b45044eebd73480
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/bb1537a5-fe7b-4c77-a582-10a82435fbc2
