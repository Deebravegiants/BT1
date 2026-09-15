# [H] Matrix iOS SDK vulnerable to impersonation via forwarded Megolm sessions

## Summary
Severity: High
Advisory: CVE-2022-39257
Aliases: GHSA-qxr3-5jmq-xcf4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-09-28
Source: https://osv.dev/vulnerability/CVE-2022-39257
Type: osv

## Details
Matrix iOS SDK allows developers to build iOS apps compatible with Matrix. Prior to version 0.23.19, an attacker cooperating with a malicious homeserver can construct messages appearing to have come from another person. Such messages will be marked with a grey shield on some platforms, but this may be missing in others. This attack is possible due to the matrix-ios-sdk implementing a too permissive key forwarding strategy. The default policy for accepting key forwards has been made more strict in the matrix-ios-sdk version 0.23.19. matrix-ios-sdk will now only accept forwarded keys in response to previously issued requests and only from own, verified devices. The SDK now sets a `trusted` flag on the decrypted message upon decryption, based on whether the key used to decrypt the message was received from a trusted source. Clients need to ensure that messages decrypted with a key with `trusted = false` are decorated appropriately (for example, by showing a warning for such messages). This attack requires coordination between a malicious home server and an attacker, so those who trust their home servers do not need a workaround.

## References
- https://github.com/matrix-org/matrix-ios-sdk/releases/tag/v0.23.19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39257.json
- https://github.com/matrix-org/matrix-ios-sdk/security/advisories/GHSA-qxr3-5jmq-xcf4
- https://nvd.nist.gov/vuln/detail/CVE-2022-39257
- https://github.com/matrix-org/matrix-ios-sdk/commit/5ca86c328a5faaab429c240551cb9ca8f0f6262c
- https://matrix.org/blog/2022/09/28/upgrade-now-to-address-encryption-vulns-in-matrix-sdks-and-clients
