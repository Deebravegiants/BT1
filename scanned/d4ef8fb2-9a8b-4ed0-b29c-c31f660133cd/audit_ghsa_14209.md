# [M] Cross-site Scripting (XSS) in pimcore via DataObject Class date fields

## Summary
Severity: Medium
Advisory: GHSA-x9xj-pqmv-8jf7
CVE: CVE-2023-2327
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-x9xj-pqmv-8jf7
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/fb3056a21d439135480ee299bf1ab646867b5f4f.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/fb3056a21d439135480ee299bf1ab646867b5f4f.patch manually.

### References
https://huntr.dev/bounties/7336b71f-a36f-4ce7-a26d-c8335ac713d6/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-x9xj-pqmv-8jf7
- https://nvd.nist.gov/vuln/detail/CVE-2023-2327
- https://github.com/pimcore/pimcore/commit/fb3056a21d439135480ee299bf1ab646867b5f4f
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/7336b71f-a36f-4ce7-a26d-c8335ac713d6
