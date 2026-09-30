# [C] PHPECC vulnerable to multiple cryptographic side-channel attacks

## Summary
Severity: Critical
Advisory: GHSA-346h-749j-r28w
CWE: CWE-203, CWE-354
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-346h-749j-r28w
Type: github-advisory

## Affected
- Packagist: `mdanter/ecc` — affected >=0

## Details
### ECDSA Canonicalization

PHPECC is vulnerable to malleable ECDSA signature attacks. 

### Constant-Time Signer

When generating a new ECDSA signature, the GMPMath adapter was used. This class wraps the GNU Multiple Precision arithmetic library (GMP), which does not aim to provide constant-time implementations of algorithms.

An attacker capable of triggering many signatures and studying the time it takes to perform each operation would be able to leak the secret number, `k`, and thereby learn the private key.

### EcDH Timing Leaks

When calculating a shared secret using the `EcDH` class, the scalar-point multiplication is based on the arithmetic defined by the `Point` class.

Even though the library implements a Montgomery ladder, the `add()`, `mul()`, and `getDouble()` methods on the `Point` class are not constant-time. This means that your ECDH private keys are leaking information about each bit of your private key through a timing side-channel.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mdanter/ecc/2024-04-24.yaml
- https://github.com/paragonie/phpecc/releases/tag/v2.0.0
- https://github.com/phpecc/phpecc
