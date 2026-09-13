# [M] matrix-sdk-crypto vulnerable to sender of encrypted events being spoofed by homeserver administrator

## Summary
Severity: Medium
Advisory: GHSA-x958-rvg6-956w
CVE: CVE-2025-48937
CWE: CWE-290
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-x958-rvg6-956w
Type: github-advisory

## Affected
- crates.io: `matrix-sdk-crypto` — affected >=0.8.0 <0.11.1

## Details
### Summary

matrix-sdk-crypto since version 0.8.0 up to 0.11.0 does not correctly validate the sender of an encrypted event. Accordingly, a malicious homeserver operator can modify events served to clients, making those events appear to the recipient as if they were sent by another user.

Although the CVSS score is 4.9 (AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N), we consider this a High Severity security issue.

### Details

The Matrix specification [requires](https://spec.matrix.org/v1.14/client-server-api/#mmegolmv1aes-sha2) that clients ensure that "the event’s `sender`, `room_id`, and the recorded `session_id` match a trusted session". The vulnerable matrix-sdk-crypto versions check that the `room_id` matches that of the session denoted by `session_id`, but do not check the `sender`.

### Patches

The issue is resolved by [13c1d20](https://github.com/matrix-org/matrix-rust-sdk/commit/13c1d2048286bbabf5e7bc6b015aafee98f04d55), included in versions 0.11.1 and 0.12.0 of matrix-sdk-crypto.

### Workarounds

Since a successful attack requires administrator access to the homeserver, users who trust the administrators of their local homeserver are not affected.

### References

 * https://spec.matrix.org/v1.14/client-server-api/#mmegolmv1aes-sha2

## References
- https://github.com/matrix-org/matrix-rust-sdk/security/advisories/GHSA-x958-rvg6-956w
- https://nvd.nist.gov/vuln/detail/CVE-2025-48937
- https://github.com/matrix-org/matrix-rust-sdk/commit/13c1d2048286bbabf5e7bc6b015aafee98f04d55
- https://github.com/matrix-org/matrix-rust-sdk/commit/56980745b4f27f7dc72ac296e6aa003e5d92a75b
- https://github.com/matrix-org/matrix-rust-sdk
- https://rustsec.org/advisories/RUSTSEC-2025-0041.html
- https://spec.matrix.org/v1.14/client-server-api/#mmegolmv1aes-sha2
