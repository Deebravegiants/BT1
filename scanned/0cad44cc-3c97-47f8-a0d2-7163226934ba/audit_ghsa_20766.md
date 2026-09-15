# [H] matrix-android-sdk2 vulnerable to impersonation via forwarded Megolm sessions

## Summary
Severity: High
Advisory: GHSA-2pvj-p485-cp3m
CVE: CVE-2022-39246
CWE: CWE-287, CWE-322
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-2pvj-p485-cp3m
Type: github-advisory

## Affected
- Maven: `org.matrix.android:matrix-android-sdk2` — affected >=0 <1.5.1

## Details
### Impact
An attacker cooperating with a malicious homeserver can construct messages appearing to have come from another person. Such messages will be marked with a grey shield on some platforms, but this may be missing in others.

This attack is possible due to the matrix-android-sdk2 implementing a too permissive [key forwarding](https://spec.matrix.org/v1.3/client-server-api/#key-requests) strategy on the receiving end.

Key forwarding is a mechanism allowing clients to recover from “unable to decrypt” messages when they missed the initial key distribution, at the time the message was originally sent. Examples include accessing message history before they joined the room but also when some network/federation errors have occurred.

### Patches

The default policy for accepting key forwards has been made more strict in the matrix-android-sdk2. The matrix-android-sdk2 will now only accept forwarded keys in response to previously issued requests and only from own, verified devices.

A unique exception to this rule is with the experimental [MSC3061](https://github.com/matrix-org/matrix-spec-proposals/pull/3061), that is forwarding room keys for past messages when invited in a room configured with the proper history visibility setting. Such key forwards are parked upon receipt and are only accepted if the SDK receives an invitation for that room from the inviter in a limited time window. 

The SDK now sets a `trusted` flag on the decrypted message upon decryption, based on whether the key used to decrypt the message was received from a trusted source. Clients need to ensure that messages decrypted with a key with `trusted = false` are decorated appropriately (for example, by showing a warning for such messages).

### Workarounds
Current users of the SDK can disable key forwarding in their forks using `CryptoService#enableKeyGossiping(enable: Boolean)`.

### References
Blog post: https://matrix.org/blog/2022/09/28/upgrade-now-to-address-encryption-vulns-in-matrix-sdks-and-clients

### For more information
If you have any questions or comments about this advisory, e-mail us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-android-sdk2/security/advisories/GHSA-2pvj-p485-cp3m
- https://nvd.nist.gov/vuln/detail/CVE-2022-39246
- https://github.com/matrix-org/matrix-spec-proposals/pull/3061
- https://github.com/matrix-org/matrix-android-sdk2/commit/77df720a238d17308deab83ecaa37f7a4740a17e
- https://github.com/matrix-org/matrix-android-sdk2
- https://github.com/matrix-org/matrix-android-sdk2/releases/tag/v1.5.1
