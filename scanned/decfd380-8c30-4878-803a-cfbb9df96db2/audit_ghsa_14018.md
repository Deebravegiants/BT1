# [M] Pimcore Cross-site Scripting (XSS) in name field of Custom Reports

## Summary
Severity: Medium
Advisory: GHSA-m6m9-gr85-79vm
CVE: CVE-2023-2614
Ecosystem: Packagist
Published: 2023-05-10
Source: https://github.com/advisories/GHSA-m6m9-gr85-79vm
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.21 or apply this patch manually:
https://github.com/pimcore/pimcore/commit/c36ef54ce33f7b5e74b7b0ab9eabfed47c018fc7.patch

### Workarounds
Apply patches manually:
https://github.com/pimcore/pimcore/commit/c36ef54ce33f7b5e74b7b0ab9eabfed47c018fc7.patch

### References
https://huntr.dev/bounties/1a5e6c65-2c5e-4617-9411-5b47a7e743a6/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-m6m9-gr85-79vm
- https://nvd.nist.gov/vuln/detail/CVE-2023-2614
- https://github.com/pimcore/pimcore/commit/c36ef54ce33f7b5e74b7b0ab9eabfed47c018fc7
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/1a5e6c65-2c5e-4617-9411-5b47a7e743a6
