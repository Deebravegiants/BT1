# [M] Pimcore vulnerable to Reflected XSS in Predefined Properties module in Settings

## Summary
Severity: Medium
Advisory: GHSA-7r35-chv4-xr3r
CVE: CVE-2023-1701
CWE: CWE-79
Ecosystem: Packagist
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-7r35-chv4-xr3r
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.20

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.20 or apply this patch manually https://github.com/pimcore/pimcore/pull/14721.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14721.patch manually.

### References
https://huntr.dev/bounties/64f943c4-68e5-4ef8-82f6-9c4abe928256/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-7r35-chv4-xr3r
- https://nvd.nist.gov/vuln/detail/CVE-2023-1701
- https://github.com/pimcore/pimcore/pull/14721.patch
- https://github.com/pimcore/pimcore/commit/2b997737dd6a60be2239a51dd6d9ef5881568e6d
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/64f943c4-68e5-4ef8-82f6-9c4abe928256
