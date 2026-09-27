# [M] Matrix Rust SDK: Sender-binding gaps in to-device and room-key attribution

## Summary
Severity: Medium
Advisory: GHSA-wfq4-36m3-9g42
CVE: CVE-2026-45056
CWE: CWE-290
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-wfq4-36m3-9g42
Type: github-advisory

## Affected
- crates.io: `matrix-sdk-crypto` — affected >=0.12.0 <0.16.1

## Details
### Impact

The `matrix-sdk-crypto` crate before 0.16.1 is missing a check for the sender's user ID when decrypting an Olm-encrypted to-device message containing the `sender_device_keys` property.

This could be exploited to spoof the sender of an encrypted to-device message, but only if the attacker colludes with (or is) the homeserver operator.

### Patches

This issue is fixed in `matrix-sdk-crypto` 0.16.1.

### Workarounds

There are no known workarounds for the issue.

### References

This issue was fixed in https://github.com/matrix-org/matrix-rust-sdk/pull/6553.

### For more information

If you have any questions or comments about this advisory, please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-rust-sdk/security/advisories/GHSA-wfq4-36m3-9g42
- https://github.com/matrix-org/matrix-rust-sdk/pull/6553
- https://github.com/matrix-org/matrix-rust-sdk
- https://github.com/matrix-org/matrix-rust-sdk/releases/tag/matrix-sdk-0.16.1
- https://rustsec.org/advisories/RUSTSEC-2026-0159.html
