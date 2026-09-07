# [M] Cross-site Scripting (XSS) in Website Settings name field

## Summary
Severity: Medium
Advisory: GHSA-2c67-p4xh-m34w
CVE: CVE-2023-2342
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-2c67-p4xh-m34w
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.21 or apply this patches manually
https://github.com/pimcore/pimcore/commit/07a2c95be524c7e20105cef58c5767d4ebb06091.patch
https://github.com/pimcore/pimcore/commit/42a5bbe5f16b97371fdbfdcf2bb3ee759dea8564.patch

### Workarounds
Apply patches manually:
https://github.com/pimcore/pimcore/commit/07a2c95be524c7e20105cef58c5767d4ebb06091.patch
https://github.com/pimcore/pimcore/commit/42a5bbe5f16b97371fdbfdcf2bb3ee759dea8564.patch

### References
https://huntr.dev/bounties/01cd3ed5-dce8-4021-9de0-81cb14bf1829/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-2c67-p4xh-m34w
- https://nvd.nist.gov/vuln/detail/CVE-2023-2342
- https://github.com/pimcore/pimcore/commit/42a5bbe5f16b97371fdbfdcf2bb3ee759dea8564
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/01cd3ed5-dce8-4021-9de0-81cb14bf1829
