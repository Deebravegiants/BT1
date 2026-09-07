# [H] PocketMine-MP server crash due to incorrect EC curve used for LoginPacket identityPublicKey

## Summary
Severity: High
Advisory: GHSA-79rc-jjh6-rc89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-14
Source: https://github.com/advisories/GHSA-79rc-jjh6-rc89
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=5.2.0 <5.3.1

## Details
### Impact
The server uses ECDH to calculate a shared secret for the symmetric encryption key used to encrypt network packets after logging in. ECDH requires that the keys used must both belong to the same elliptic curve. In Minecraft: Bedrock Edition, the curve used is `secp384r1`.

Using any other curve (for example `secp256r1`) to sign the `LoginPacket` JWTs would lead to successfully verifying the login chain, but would later crash due to an uncaught exception during ECDH key derivation due to the client-provided key belonging to a different curve than the server's key. It's also theoretically possible that a non-EC key could be used (e.g. RSA or DH), which would also pass login verification as long as SHA384 hashing algorithm was used for the JWT signatures, and also lead to a crash.

### Patches
The problem was fixed in 4.23.1 and 5.3.1 in the following commit: 4e646d19a4a1e0d082bd4d1f5a58ae0182a268d9
While 4.x would not have crashed when this was encountered, the faulty validation code has also been corrected there.

### Workarounds
A plugin could handle `LoginPacket` and check that all of the `identityPublicKey`s provided in the JWT bodies actually belong to `secp384r1`. This can be checked by verifying that `openssl_pkey_get_details($key)["ec"]["curve_name"]` is set and equal to `secp384r1`. Beware that this element may not exist if the key is not an EC key at all.

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-79rc-jjh6-rc89
- https://github.com/pmmp/PocketMine-MP/commit/4e646d19a4a1e0d082bd4d1f5a58ae0182a268d9
- https://github.com/pmmp/PocketMine-MP
