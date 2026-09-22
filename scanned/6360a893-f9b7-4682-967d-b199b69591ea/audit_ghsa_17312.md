# [M] Zitadel Discloses the Total Number of Instance Users

## Summary
Severity: Medium
Advisory: GHSA-f4cf-9rvr-2rcx
CVE: CVE-2025-67717
CWE: CWE-497
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-f4cf-9rvr-2rcx
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=4.0.0-rc.1 <4.7.2
- Go: `github.com/zitadel/zitadel` — affected >=2.44.0 <3.4.5
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20251210121356-826039c6208f

## Details
### Summary

Zitadel's User Service discloses the total number of instance users to unauthorized users.

### Impact

The ZITADEL User Service exposes the total number of users within an instance to any authenticated user, regardless of their specific permissions. While this does not leak individual user data or PII, disclosing the total user count via the `totalResult` field constitutes an information disclosure vulnerability that may be sensitive in certain contexts.

### Affected Versions

Systems running one of the following version are affected:

- **4.x**: `4.0.0-rc.1` through `4.7.1`
- **3.x**: `3.0.0-rc.1` through `3.4.4`
- **2.x**: `2.44.0` through `2.71.19`

### Patches

The vulnerability has been addressed in the latest release. The patch resolves the issue and returns the `totalResult` value corresponding to the number of instance users for whom the querying user has read permission.

- 4.x: Upgrade to >= [4.7.2](https://github.com/zitadel/zitadel/releases/tag/v4.7.2)
- 3.x: Update to >= [3.4.5](https://github.com/zitadel/zitadel/releases/tag/v3.4.5)
- 2.x: Update to >= [3.4.5](https://github.com/zitadel/zitadel/releases/tag/v3.4.5) (or checkout the workarounds section)

### Workarounds

The recommended solution is to update Zitadel to a patched version.

If a version upgrade is not possible, you can enable the `permissionCheckV2` feature on your instance.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

This vulnerability was found by [zentrust partners GmbH](https://zentrust.partners) during a scheduled penetration test. Thank you to the analysts Martin Tschirsich, Joud Zakharia, Christopher Baumann.
The full report will be made public after the complete review.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-f4cf-9rvr-2rcx
- https://nvd.nist.gov/vuln/detail/CVE-2025-67717
- https://github.com/zitadel/zitadel/commit/826039c6208fe71df57b3a94c982b5ac5b0af12c
- https://github.com/zitadel/zitadel
