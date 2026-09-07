# [M] Reflected XSS in Application Logger module

## Summary
Severity: Medium
Advisory: GHSA-2xpm-cmvw-3jcc
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-16
Source: https://github.com/advisories/GHSA-2xpm-cmvw-3jcc
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.

### Patches
Update to version 10.5.19 or apply this patch manually https://github.com/pimcore/pimcore/pull/14606.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14606.patch manually.

### References
https://huntr.dev/bounties/2a64a32d-b1cc-4def-91da-18040d59f356/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-2xpm-cmvw-3jcc
- https://nvd.nist.gov/vuln/detail/CVE-2023-1312
- https://github.com/pimcore/pimcore/pull/14606
- https://github.com/pimcore/pimcore/pull/14606.patch
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/2a64a32d-b1cc-4def-91da-18040d59f356
