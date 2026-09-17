# [H] matrix-js-sdk subject to user spoofing via Olm/Megolm protocol confusion

## Summary
Severity: High
Advisory: GHSA-r48r-j8fx-mq2c
CVE: CVE-2022-39251
CWE: CWE-287, CWE-322
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-r48r-j8fx-mq2c
Type: github-advisory

## Affected
- npm: `matrix-js-sdk` — affected >=0 <19.7.0

## Details
### Impact

An attacker cooperating with a malicious homeserver can construct messages that legitimately appear to have come from another person, without any indication such as a grey shield.

Additionally, a sophisticated attacker cooperating with a malicious homeserver could employ this vulnerability to perform a targeted attack in order to send fake to-device messages appearing to originate from another user. This can allow, for example, to inject the key backup secret during a self-verification, to make a targeted device start using a malicious key backup spoofed by the homeserver.

These attacks are possible due to a protocol confusion vulnerability that accepts to-device messages encrypted with Megolm instead of Olm.

### Patches

matrix-js-sdk has been modified to only accept Olm-encrypted to-device messages.

Out of caution, several other checks have been audited or added:
- Cleartext `m.room_key`, `m.forwarded_room_key` and `m.secret.send` to_device messages are discarded.
- Secrets received from untrusted devices are discarded.
- Key backups are only usable if they have a valid signature from a trusted device (no more local trust, or trust-on-decrypt).
- The origin of a to-device message should only be determined by observing the Olm session which managed to decrypt the message, and not by using claimed sender_key, user_id, or any other fields controllable by the homeserver.

### Workarounds

As this attack requires coordination between a malicious home server and an attacker, if you trust your home server no particular workaround is needed. Notice that the backup spoofing attack is a particularly sophisticated targeted attack.

We are not aware of this attack being used in the wild, though specifying a false positive-free way of noticing malicious key backups key is challenging.

As an abundance of caution, to avoid malicious backup attacks, you should not verify your new logins using emoji/QR verifications methods until patched. Prefer verifying with your security passphrase instead.

### References
Blog post: https://matrix.org/blog/2022/09/28/upgrade-now-to-address-encryption-vulns-in-matrix-sdks-and-clients

### For more information
If you have any questions or comments about this advisory, e-mail us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-r48r-j8fx-mq2c
- https://nvd.nist.gov/vuln/detail/CVE-2022-39251
- https://github.com/matrix-org/matrix-js-sdk/commit/a587d7c36026fe1fcf93dfff63588abee359be76
- https://github.com/matrix-org/matrix-js-sdk
- https://github.com/matrix-org/matrix-js-sdk/releases/tag/v19.7.0
- https://matrix.org/blog/2022/09/28/upgrade-now-to-address-encryption-vulns-in-matrix-sdks-and-clients
- https://security.gentoo.org/glsa/202210-35
