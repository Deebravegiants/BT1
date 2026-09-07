# [M] Cross-site Scripting (XSS) - stored in Print Documents

## Summary
Severity: Medium
Advisory: GHSA-rrwm-8wqm-gwgv
CWE: CWE-79
Ecosystem: Packagist
Published: 2023-03-16
Source: https://github.com/advisories/GHSA-rrwm-8wqm-gwgv
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact
Stored xss leads to steal cookies and other information of other users

### Patches
Update to version 10.5.19 or apply this patch manually https://github.com/pimcore/pimcore/pull/14560.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14560.patch manually.

### References
https://huntr.dev/bounties/31d97442-3f87-439f-83f0-1c7862ef0c7c/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-rrwm-8wqm-gwgv
- https://github.com/pimcore/pimcore
