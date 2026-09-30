# [M] `Slip10Like` derivation method instantiated with certain curves may allow attacker to find derivation path which results into very long derivation (possible DoS)

## Summary
Severity: Medium
Advisory: GHSA-2ff4-xfpr-m32r
Ecosystem: crates.io
Published: 2024-12-18
Source: https://github.com/advisories/GHSA-2ff4-xfpr-m32r
Type: github-advisory

## Affected
- crates.io: `hd-wallet` — affected >=0 <0.6.0
- crates.io: `slip-10` — affected >=0

## Details
### Impact
<!-- _What kind of vulnerability is it? Who is impacted?_ -->

**Impacted are the only ones who use [`hd_wallet::Slip10Like`](https://docs.rs/hd-wallet/0.5.1/hd_wallet/struct.Slip10Like.html) or [`slip_10`](https://docs.rs/slip-10/latest/slip_10/) derivation method instantiated with curves other than secp256k1 and secp256r1.**

`hd_wallet` crate used to provide `Slip10Like` derivation method, which is also provided in `slip-10` crate as a default derivation method. It's based on [slip10](https://github.com/satoshilabs/slips/blob/master/slip-0010.md) method that searches for a valid child key in an infinite loop until it's found.

Theoretically, this could be exploited by an attacker by finding a derivation path that would force someone to execute a lot of iterations of this loop to find a valid child key. This attack, however, requires the probability of getting an invalid scalar from random 32 bytes to be high. Slip10 is protected from this attack as it's only defined on secp256k1 and secp256r1 curves, for which such probability is very low:

- For secp256k1, probability is $< 2^{-127}$. This means that a loop with 2 or more iterations is vanishingly impossible.
- For secp256r1, probability is $< 2^{-32}$. This means that a loop with 5 or more iterations is vanishingly impossible.

While standard curves are safe to use with slip10, we used to allow slip10-like derivation which can be instantiated with any curve. For instance, one could instantiate it with ed25519 or stark curves, for which probability of getting invalid scalar from random 32 bytes is >90%, so theoretically, attacker could try to DoS such construction.

### Patches
<!-- _Has the problem been patched? What versions should users upgrade to?_ -->

`hd_wallet v0.6.0` has been patched by removing slip10-like derivation from public API.

If you need HD derivation on other curves than secp256k1 and secp256r1, we suggest you to use:
* [`hd_wallet::Edwards`](https://docs.rs/hd-wallet/latest/hd_wallet/edwards/struct.Edwards.html) derivation method available for ed25519 curve
* [`hd_wallet::Stark`](https://docs.rs/hd-wallet/latest/hd_wallet/stark/struct.Stark.html) derivation method available for stark curve

Both derivation methods are non-standard, but secure and efficient.

**If you're still using `slip_10`** and would like to migrate to patched version, please migrate to `hd_wallet v0.6`. You may first migrate from `slip_10 v0.4` to `hd_wallet v0.5` by following migration instructions available [in the docs](https://docs.rs/slip-10/latest/slip_10/), and then upgrade from `hd_wallet v0.5` to `hd_wallet v0.6`.

### Workarounds
Technically, you don't need to upgrade if you don't use slip10-like derivation instantiated with other curves than secp256k1 or secp256r1.

However, if you do, migrating to other derivation method might be required.

### Reach out to us in Discord

If you want to reach out to us, feel free to write to [`#lockness` room in Discord](https://discordapp.com/channels/905194001349627914/1294284489635139585)

### Credits

Thanks to Alessio Marziali <alessio.marziali@metaco.com> for discovering and flagging this issue

## References
- https://github.com/LFDT-Lockness/hd-wallet/security/advisories/GHSA-2ff4-xfpr-m32r
- https://github.com/LFDT-Lockness/hd-wallet/commit/a7e37704600ee7c737dbb02db08814dd2d15389d
- https://github.com/LFDT-Lockness/hd-wallet
