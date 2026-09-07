# [M] matrix-js-sdk will freeze when a user sets a room with itself as a its predecessor

## Summary
Severity: Medium
Advisory: GHSA-vhr5-g3pm-49fm
CVE: CVE-2024-42369
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2024-08-20
Source: https://github.com/advisories/GHSA-vhr5-g3pm-49fm
Type: github-advisory

## Affected
- npm: `matrix-js-sdk` — affected >=0 <34.3.1

## Details
### Impact
A malicious homeserver can craft a room or room structure such that the predecessors form a cycle. The matrix-js-sdk's `getRoomUpgradeHistory` function will infinitely recurse in this case, causing the code to hang. This method is public but also called by the 'leaveRoomChain()' method, so leaving a room will also trigger the bug.

Even if the CVSS score would be 4.1 ([AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:N/A:L](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:N/A:L&version=3.1)) we classify this as High severity issue.

### Patches
This was patched in matrix-js-sdk 34.3.1.

### Workarounds
Sanity check rooms before passing them to the matrix-js-sdk or avoid calling either `getRoomUpgradeHistory` or `leaveRoomChain`.

### References
N/A.

## References
- https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-vhr5-g3pm-49fm
- https://nvd.nist.gov/vuln/detail/CVE-2024-42369
- https://github.com/matrix-org/matrix-js-sdk/commit/a0efed8b881b3db6c9f2c71d6a6e74c2828978c6
- https://github.com/matrix-org/matrix-js-sdk
