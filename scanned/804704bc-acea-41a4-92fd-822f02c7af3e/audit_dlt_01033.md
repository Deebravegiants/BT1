# [C] tss-lib leaks secret keys in response to incorrectly constructed Paillier moduli

## Summary
Severity: Critical
Chain: github.com/bnb-chain/tss-lib
Component: github.com/bnb-chain/tss-lib
CWE: Exposure of Sensitive Information to an Unauthorized Actor
Published: 2023-09-01
Source: https://github.com/advisories/GHSA-h24c-6p6p-m3vx
Type: github-advisory

## Details
### Impact

The specification of the GG18 threshold ECDSA signature protocol contains a vulnerability allowing an attacker to recover the shared secret key. If a participant generates a Paillier modulus `N` containing small factors (less than `2^100`) they can interact with other participants in the signing protocol to steal their secret key shares in as little as sixteen signing attempts. The master key can then be reconstructed from these shares.

### Patches

The implementation of GG18 in tss-lib did not prove that `N` is biprime or that it doesn't contain small factors. The fixed implementation adds the following proofs from the CGGMP21 threshold ECDSA protocol to the key generation:

- Paillier-Blum Modulus (`N` is the product of two primes)
- No Small Factor (both factors of `N` are greater than `2^256`)

These proofs apply to both the Paillier encryption modulus `N`, and the modulus `NTilde` used in MTA proofs.

To address the issue in the resharing protocol, an additional round has been added to the end so that participants can confirm that they received valid proofs.

### References

- [GG18](https://eprint.iacr.org/2019/114)
- [CGGMP21](https://eprint.iacr.org/2021/060)
