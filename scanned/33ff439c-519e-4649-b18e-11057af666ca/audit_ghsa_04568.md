# [M] matrix-sdk-ui: Incomplete edit validation

## Summary
Severity: Medium
Advisory: GHSA-h97m-27fx-42rx
CVE: CVE-2026-45057
CWE: CWE-345
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-h97m-27fx-42rx
Type: github-advisory

## Affected
- crates.io: `matrix-sdk-ui` — affected >=0 <0.16.1

## Details
### Impact
The message edit validation logic in the  `matrix-sdk-ui` crate before 0.16.1 is missing a check: when replacing an encrypted event, the replacement event itself is not required to be encrypted. This enables a malicious homeserver administrator (or an actor with equivalent power) to impersonate or spoof messages as if they were sent by a victim user.

### Patches
`matrix-sdk-ui` 0.16.1 fixes the message edit validation logic to align with the algorithm for replacement events[^1] described in the Matrix specification.

### Workarounds
N/A

### References
* Pull request: https://github.com/matrix-org/matrix-rust-sdk/pull/6454

### For more information
If you have any questions or comments about this advisory, please email us at [security at matrix.org](mailto:security@matrix.org).

[^1]: https://spec.matrix.org/unstable/client-server-api/#validity-of-replacement-events

## References
- https://github.com/matrix-org/matrix-rust-sdk/security/advisories/GHSA-h97m-27fx-42rx
- https://github.com/matrix-org/matrix-rust-sdk/pull/6454
- https://github.com/matrix-org/matrix-rust-sdk
- https://github.com/matrix-org/matrix-rust-sdk/releases/tag/matrix-sdk-0.16.1
- https://rustsec.org/advisories/RUSTSEC-2026-0158.html
