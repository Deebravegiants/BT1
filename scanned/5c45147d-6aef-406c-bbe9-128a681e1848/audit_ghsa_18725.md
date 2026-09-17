# [M] gnark-crypto doesn't range check input values during ECDSA and EdDSA signature deserialization

## Summary
Severity: Medium
Advisory: GHSA-fr8m-434r-g3xp
CVE: CVE-2023-44273
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-fr8m-434r-g3xp
Type: github-advisory

## Affected
- Go: `github.com/consensys/gnark-crypto` — affected >=0 <0.12.0

## Details
### Impact

During deserialization of ECDSA and EdDSA signatures gnark-crypto did not check that the values are in the range `[1, n-1]` with `n` being the corresponding modulus (either base field modulus in case of `R` in EdDSA, and scalar field modulus in case of `s,r` in ECDSA and `s` in EdDSA). As this also allowed zero inputs, then it was possible to craft a signature which lead to null pointer dereference, leading to denial-of-service of an application. This also enabled weak signature malleability when the users assumed uniqueness of the serialized signatures (but not the underlying modulo reduced values).

We are not aware of any users impacted by the bug. The implemented signature schemes in gnark-crypto complement the in-circuit versions in gnark, allowing to have end-to-end tests.

### Patches

The issue was patched in PR #449. The fix returns an error during deserialization if the values do not belong to the ranges `[1, n-1]`.

The fix is included in release v0.12.0 and upwards.

### Workarounds

Users can manually validate the inputs to be in corresponding ranges when using serialized signatures (or digests of them) as unique keys.

To address the denial-of-service, the users can install hook to recover panics and recover 

### Resources

* [Verichains advisory](https://github.com/advisories/GHSA-9xfq-8j3r-xp5g) for signature malleability.
* Fix https://github.com/Consensys/gnark-crypto/pull/449
* [Go blog post "Defer, Panic, and Recover"](https://go.dev/blog/defer-panic-and-recover)
* [gnark v0.12.0](https://github.com/Consensys/gnark-crypto/releases/tag/v0.12.0)


### Acknowledgement

Lack of range checks leading to signature malleability was reported by [Verichains](https://www.verichains.io/).

## References
- https://github.com/Consensys/gnark-crypto/security/advisories/GHSA-fr8m-434r-g3xp
- https://nvd.nist.gov/vuln/detail/CVE-2023-44273
- https://github.com/Consensys/gnark-crypto/pull/449
- https://github.com/Consensys/gnark-crypto
- https://github.com/Consensys/gnark-crypto/releases/tag/v0.12.0
- https://go.dev/blog/defer-panic-and-recover
