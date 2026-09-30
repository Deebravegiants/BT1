# [H] PQClean has a correctness error in HQC decapsulation

## Summary
Severity: High
Advisory: GHSA-753p-wrj5-g8fj
CWE: CWE-1240, CWE-200
Ecosystem: crates.io
Published: 2024-12-11
Source: https://github.com/advisories/GHSA-753p-wrj5-g8fj
Type: github-advisory

## Affected
- crates.io: `pqcrypto-hqc` — affected >=0 <0.2.1

## Details
### Impact

A correctness error has been identified in the reference implementation of the HQC key encapsulation mechanism. Due to an indexing error, part of the secret key is incorrectly treated as non-secret data. This results in an incorrect shared secret value being returned when the decapsulation function is called with a malformed ciphertext.

No concrete attack exploiting the error has been identified at this point. However, the error involves mishandling of the secret key, and in principle this presents a security vulnerability.

### Patches

PQClean does not have a release process, as it is a collection of implementations. If you obtained a HQC implementation from PQClean, please update to a version that includes the fixes proposed in https://github.com/PQClean/PQClean/pull/578. 

Please also [refer to our security policy](https://github.com/PQClean/PQClean/blob/master/SECURITY.md).

### Workarounds

Manually patching is always possible

### Further details

In the 2023/04/30 version of the HQC specification and reference implementation, an extra field (sigma) was added to the secret key structure to enable implicit rejection of malformed ciphertexts. The logic to retrieve the public key from the secret key in the decapsulation function was not updated accordingly. As a result, sigma is treated as part of the public key. Later in the decapsulation call, a incorrectly constructed comparison check allows this error to go through undetected. Due to how these two bugs interfere with each other, the decapsulation function never uses sigma to perform implicit rejection; instead, it accepts malformed ciphertexts and returns shared secrets based on their decryptions.

### References

This issue was first reported in OQS https://github.com/open-quantum-safe/liboqs/security/advisories/GHSA-gpf4-vrrw-r8v7. The vulnerability was identified by Célian Glénaz and Dahmun Goudarzi (Quarkslab).

## References
- https://github.com/PQClean/PQClean/security/advisories/GHSA-753p-wrj5-g8fj
- https://github.com/open-quantum-safe/liboqs/security/advisories/GHSA-gpf4-vrrw-r8v7
- https://github.com/PQClean/PQClean/pull/578
- https://github.com/rustpq/pqcrypto/commit/0c07fa8badbf44f67d3ff1571df31ca54e5228c0
- https://github.com/PQClean/PQClean
