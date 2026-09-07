# [M] Cross-site Scripting (XSS) in Document Properties Parameter

## Summary
Severity: Medium
Advisory: GHSA-476g-v7hf-cw5m
CVE: CVE-2023-2322
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-476g-v7hf-cw5m
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/9fc674892b8b53103098b9524705074a45e7f773.patch


### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/9fc674892b8b53103098b9524705074a45e7f773.patch manually.

### References
https://huntr.dev/bounties/f7228f3f-3bef-46fe-b0e3-56c432048a67/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-476g-v7hf-cw5m
- https://nvd.nist.gov/vuln/detail/CVE-2023-2322
- https://github.com/pimcore/pimcore/commit/9fc674892b8b53103098b9524705074a45e7f773
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/f7228f3f-3bef-46fe-b0e3-56c432048a67
