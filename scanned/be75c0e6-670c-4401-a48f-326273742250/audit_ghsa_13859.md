# [M] Cross Site Scripting (XSS) in Model\DataObject\Data\UrlSlug

## Summary
Severity: Medium
Advisory: GHSA-76r7-h46w-463r
CWE: CWE-79
Ecosystem: Packagist
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-76r7-h46w-463r
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.17

## Details
### Impact
An attacker can use XSS to send a malicious script to an unsuspecting user.

### Patches
Update to version 10.5.17 or apply this patch manually https://github.com/pimcore/pimcore/pull/14301.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14301.patch manually.

### References
https://huntr.dev/bounties/75bc7d07-46a7-4ed9-a405-af4fc47fb422/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-76r7-h46w-463r
- https://github.com/pimcore/pimcore
