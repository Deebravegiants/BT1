# [M] File upload local preview can run embedded scripts after user interaction

## Summary
Severity: Medium
Advisory: GHSA-8796-gc9j-63rv
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-8796-gc9j-63rv
Type: github-advisory

## Affected
- npm: `matrix-react-sdk` — affected >=0 <3.21.0

## Details
### Impact

When uploading a file, the local file preview can lead to execution of scripts embedded in the uploaded file, but only after several user interactions to open the preview in a separate tab. This only impacts the local user while in the process of uploading. It cannot be exploited remotely or by other users.

### Patches

This has been fixed by https://github.com/matrix-org/matrix-react-sdk/pull/5981, which is included in 3.21.0.

### Workarounds

There are no known workarounds.

## References
- https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-8796-gc9j-63rv
- https://github.com/matrix-org/matrix-react-sdk
