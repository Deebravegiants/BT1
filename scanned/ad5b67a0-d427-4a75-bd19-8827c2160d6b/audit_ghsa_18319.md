# [M] matrix-js-sdk has insufficient validation when considering a room to be upgraded by another

## Summary
Severity: Medium
Advisory: GHSA-mp7c-m3rh-r56v
CVE: CVE-2025-59160
CWE: CWE-20, CWE-345, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-mp7c-m3rh-r56v
Type: github-advisory

## Affected
- npm: `matrix-js-sdk` — affected >=0 <38.2.0

## Details
### Impact
matrix-js-sdk before 38.2.0 has insufficient validation of room predecessor links in `MatrixClient::getJoinedRooms`, allowing a remote attacker to attempt to replace a tombstoned room with an unrelated attacker-supplied room.

### Patches
The issue has been patched and users should upgrade to 38.2.0.

### Workarounds
Avoid using `MatrixClient::getJoinedRooms` in favour of `getRooms()` and filtering upgraded rooms separately.

## References
- https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-mp7c-m3rh-r56v
- https://nvd.nist.gov/vuln/detail/CVE-2025-59160
- https://github.com/matrix-org/matrix-js-sdk/commit/43c72d5bf5e2d0a26b3b4f71092e7cb39d4137c4
- https://github.com/matrix-org/matrix-js-sdk
- https://github.com/matrix-org/matrix-js-sdk/releases/tag/v38.2.0
- https://www.npmjs.com/package/matrix-js-sdk/v/38.2.0
