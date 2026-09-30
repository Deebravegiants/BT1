# [M] Observable Response Discrepancy in Lost Password Service

## Summary
Severity: Medium
Advisory: GHSA-579x-cjvr-cqj9
CVE: CVE-2021-39189
CWE: CWE-203, CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-579x-cjvr-cqj9
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.1.3

## Details
### Impact
It is possible to enumerate usernames via the forgot password functionality

### Patches
Update to version `10.1.3` or apply this patch manually: https://github.com/pimcore/pimcore/pull/10223.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/10223.patch manually.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-579x-cjvr-cqj9
- https://nvd.nist.gov/vuln/detail/CVE-2021-39189
- https://github.com/pimcore/pimcore/pull/10223.patch
- https://github.com/pimcore/pimcore/pull/10223/commits/d0a4de39cf05dce6af71f8ca039132bdfcbb0dce
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/12462a99-ebf8-4e39-80b3-54a16caa3f4c
