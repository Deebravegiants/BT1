# [M] Pimcore Cross-site Scripting in Predefined Asset Metadata module in Settings

## Summary
Severity: Medium
Advisory: GHSA-6qjm-39vh-729w
CVE: CVE-2023-1702
CWE: CWE-79
Ecosystem: Packagist
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-6qjm-39vh-729w
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.20

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.20 or apply this patch manually https://github.com/pimcore/pimcore/pull/14721.patch

### Workarounds
Apply patch manually https://github.com/pimcore/pimcore/pull/14721.patch

### References
https://huntr.dev/bounties/d8a47f29-3297-4fce-b534-e1d95a2b3e19

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-6qjm-39vh-729w
- https://nvd.nist.gov/vuln/detail/CVE-2023-1702
- https://github.com/pimcore/pimcore/pull/14721.patch
- https://github.com/pimcore/pimcore/commit/2b997737dd6a60be2239a51dd6d9ef5881568e6d
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/d8a47f29-3297-4fce-b534-e1d95a2b3e19
