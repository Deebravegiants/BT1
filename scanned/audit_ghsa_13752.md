# [M] Marvin Attack: potential key recovery through timing sidechannels

## Summary
Severity: Medium
Advisory: GHSA-4grx-2x9w-596c
CWE: CWE-385
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-4grx-2x9w-596c
Type: github-advisory

## Affected
- crates.io: `rsa` — affected >=0

## Details
The [Marvin Attack] is a timing sidechannel vulnerability which allows performing RSA decryption and signing operations as an attacker with the ability to observe only the time of the decryption operation performed withthe private key.

A recent survey of RSA implementations found that the Rust `rsa` crate is one of many implementations vulnerable to this attack.

No fixed version is available at this time.

[Marvin Attack]: https://people.redhat.com/~hkario/marvin/

## References
- https://github.com/RustCrypto/RSA/security/advisories/GHSA-c38w-74pg-36hr
- https://github.com/RustCrypto/RSA/issues/19#issuecomment-1822995643
- https://github.com/RustCrypto/RSA/issues/626
- https://github.com/RustCrypto/RSA
- https://rustsec.org/advisories/RUSTSEC-2023-0071.html
