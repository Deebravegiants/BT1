# [H] Improper calculations in ECC implementation can trigger a Denial-of-Service (DoS)

## Summary
Severity: High
Advisory: GHSA-5h4j-qrvg-9xhw
CVE: CVE-2023-25653
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-16
Source: https://github.com/advisories/GHSA-5h4j-qrvg-9xhw
Type: github-advisory

## Affected
- npm: `node-jose` — affected >=0 <2.2.0

## Details
### Description

When using the non-default "fallback" crypto back-end, ECC operations in `node-jose` can trigger a Denial-of-Service (DoS) condition, due to a possible infinite loop in an internal calculation.  For some ECC operations, this condition is triggered randomly; for others, it can be triggered by malicious input.

#### Technical summary

The JOSE logic implemented by `node-jose` usually relies on an external cryptographic library for the underlying cryptographic primitives that JOSE operations require.  When WebCrypto or the Node `crypto` module are available, they are used.  When neither of these libraries is available, `node-jose` includes its own "fallback" implementations of some algorithms based on `node-forge`, in particular implementations of ECDH and ECDSA. 

A various points, these algorithm implementations need to compute to the X coordinate of an elliptic curve point.  This is done by calling the `getX()` method of the object representing the point, which is an alias of the function `pointFpGetX()` in `lib/deps/ecc/math.js`.

Computing the X coordinate from the form in which the point is stored requires computing the modular inverse of the Z coordinate, using the `modInverse` function from the `jsbn` library (e.g., `this.z.modInverse(this.curve.p)`).  The output of this function call is multiplied by another value before being reduced with the `barrettReduce()` function.

The root cause of this issue is that the `jsbn` `modInverse` function sometimes returns negative results.  These results are correct in that they are equivalent mod the relevant modulus, but can be problematic for functions that expect modular operations to always return positive results (in the range `[0, p)`, where `p` is the modulus).

In particular, while the Barrett reduction algorithm in general can handle negative inputs, the implementation in `node-jose` explicitly does not. Therefore, while the negative value that is returned by `modInverse()` is mathematically correct, it leads to an error in `barrettReduce()` causing an infinite loop which may result in a Denial of Service condition.

For a given prime modulus, we estimate that roughly one in every `2^20` inputs produce a negative `modInverse()`.  This estimate was validated with exhaustive testing on small primes (<30 bits) and randomized testing with regard to the P-256 prime.

### Impact

This issue is only present in situations where the "fallback" cryptographic implementation is being used, i.e., situations where neither WebCrypto nor the Node `crypto` module is available.

The following elliptic curve algorithms are impacted by this issue (all in `lib/deps/ecc/index.js`):

- Elliptic curve key generation (`exports.generateKeyPair`)
- Converting an elliptic curve private key to a public key (`ECPrivateKey.prototype.toPublicKey`)
- ECDSA signing (`ECPrivateKey.prototype.sign`)
- ECDSA verification (`ECPublicKey.prototype.verify`)
- ECDH key agreement (`ECPrivateKey.prototype.computeSecret`)

In the first three cases, the points being evaluated are generated randomly, so an attack could only arise due to a bad value being randomly selected (as noted above, with probability roughly `2^{-20}`).  In the latter two cases, the points being evaluated are provided from outside the library, and thus potentially by attackers.

### Patches

_Has the problem been patched? What versions should users upgrade to?_

### Workarounds

Since this issue is only present in the "fallback" crypto implementation, it can be avoided by ensuring that either WebCrypto or the Node `crypto` module is available in the JS environment where `node-jose` is being run.

### References

- [Barrett reduction on Wikipedia](https://en.wikipedia.org/wiki/Barrett_reduction)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [cisco/node-jose](https://github.com/cisco/node-jose/issues)
* Email [Cisco open source security](mailto:oss-security@cisco.com)

### Credits

- Research and disclosure: BlackBerry
- Fix implementation: [Richard Barnes (@bifurcation)](https://github.com/bifurcation)
- Release engineering: [Stephen Augustus (@justaugustus)](https://github.com/justaugustus)

## References
- https://github.com/cisco/node-jose/security/advisories/GHSA-5h4j-qrvg-9xhw
- https://nvd.nist.gov/vuln/detail/CVE-2023-25653
- https://github.com/cisco/node-jose/commit/901d91508a70e3b9bdfc45688ea07bb4e1b8210d
- https://github.com/cisco/node-jose
