# [H] Matrix JavaScript SDK's key history sharing could share keys to malicious devices

## Summary
Severity: High
Advisory: GHSA-4jf8-g8wp-cx7c
CVE: CVE-2024-47080
CWE: CWE-200, CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-4jf8-g8wp-cx7c
Type: github-advisory

## Affected
- npm: `matrix-js-sdk` — affected >=9.11.0 <34.8.0

## Details
### Impact
In matrix-js-sdk versions 9.11.0 through 34.7.0, the method `MatrixClient.sendSharedHistoryKeys` is vulnerable to interception by malicious homeservers.  The method implements functionality proposed in [MSC3061](https://github.com/matrix-org/matrix-spec-proposals/pull/3061) and can be used by clients to share historical message keys with newly invited users, granting them access to past messages in the room.

However, it unconditionally sends these "shared" keys to all of the invited user's devices, regardless of whether the user's cryptographic identity is verified or whether the user's devices are signed by that identity. This allows the attacker to potentially inject its own devices to receive sensitive historical keys without proper security checks.

Note that this only affects clients running the SDK with the legacy crypto stack. Clients using the new Rust cryptography stack (i.e. those that call `MatrixClient.initRustCrypto()` instead of `MatrixClient.initCrypto()`) are unaffected by this vulnerability, because `MatrixClient.sendSharedHistoryKeys()` raises an exception in such environments.

### Patches
Fixed in matrix-js-sdk 34.8.0 by removing the vulnerable functionality.

### Workarounds
Remove use of affected functionality from clients.

### References
- [MSC3061](https://github.com/matrix-org/matrix-spec-proposals/pull/3061)

### For more information
If you have any questions or comments about this advisory, please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-4jf8-g8wp-cx7c
- https://nvd.nist.gov/vuln/detail/CVE-2024-47080
- https://github.com/matrix-org/matrix-spec-proposals/pull/3061
- https://github.com/matrix-org/matrix-js-sdk/commit/2fb1e659c81f75253c047832dc9dcc2beddfac5f
- https://github.com/matrix-org/matrix-js-sdk
