# [M] matrix-sdk-crypto contains potential impersonation via room key forward responses

## Summary
Severity: Medium
Advisory: GHSA-vp68-2wrm-69qm
CVE: CVE-2022-39252
CWE: CWE-287
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-vp68-2wrm-69qm
Type: github-advisory

## Affected
- crates.io: `matrix-sdk-crypto` — affected >=0 <0.6.0

## Details
### Impact

When matrix-rust-sdk before 0.6 requests a room key from our devices, it correctly accepts key forwards only if they are a response to a previous request. However, it doesn't check that the device that responded matches the device the key was requested from.

This allows a malicious homeserver to insert room keys of questionable validity into the key store in some situations, potentially assisting in an impersonation attack. Note that even if key injection succeeds in this way, all forwarded keys have the `imported` flag set, which is used as an indicator that such keys have lesser authentication properties (and should be marked as such in clients, e.g. with a grey shield besides the message).

### For more information
If you have any questions or comments about this advisory, e-mail us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-rust-sdk/security/advisories/GHSA-vp68-2wrm-69qm
- https://nvd.nist.gov/vuln/detail/CVE-2022-39252
- https://github.com/matrix-org/matrix-rust-sdk/commit/093fb5d0aa21c0b5eaea6ec96b477f1075271cbb
- https://github.com/matrix-org/matrix-rust-sdk/commit/41449d2cc360e347f5d4e1c154ec1e3185f11acd
- https://github.com/matrix-org/matrix-rust-sdk
- https://github.com/matrix-org/matrix-rust-sdk/releases/tag/matrix-sdk-0.6.0
- https://rustsec.org/advisories/RUSTSEC-2022-0085.html
