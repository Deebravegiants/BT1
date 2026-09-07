# [M] pimcore is vulnerable to cross-site scripting in translate module

## Summary
Severity: Medium
Advisory: GHSA-hfmg-g39c-5444
CVE: CVE-2023-1704
CWE: CWE-79
Ecosystem: Packagist
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-hfmg-g39c-5444
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.20

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.20 or apply this patch manually https://github.com/pimcore/pimcore/pull/14732.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14732.patch manually.

### References
https://huntr.dev/bounties/84419c7b-ae29-401b-bdfd-5d0c498d320f/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-hfmg-g39c-5444
- https://nvd.nist.gov/vuln/detail/CVE-2023-1704
- https://github.com/pimcore/pimcore/pull/14732.patch
- https://github.com/pimcore/pimcore/commit/295f5e8d108b68198e36399bea0f69598eb108a0
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/84419c7b-ae29-401b-bdfd-5d0c498d320f
