# [M] Padding Oracle Attack due to Observable Timing Discrepancy in jose-node-cjs-runtime

## Summary
Severity: Medium
Advisory: GHSA-rvcw-f68w-8h8h
CVE: CVE-2021-29446
CWE: CWE-203, CWE-208, CWE-696
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-rvcw-f68w-8h8h
Type: github-advisory

## Affected
- npm: `jose-node-cjs-runtime` — affected >=0 <3.11.4

## Details
### Impact

[AES_CBC_HMAC_SHA2 Algorithm](https://tools.ietf.org/html/rfc7518#section-5.2) (A128CBC-HS256, A192CBC-HS384, A256CBC-HS512) decryption would always execute both HMAC tag verification and CBC decryption, if either failed `JWEDecryptionFailed` would be thrown. But a possibly observable difference in timing when padding error would occur while decrypting the ciphertext makes a padding oracle and an adversary might be able to make use of that oracle to decrypt data without knowing the decryption key by issuing on average 128*b calls to the padding oracle (where b is the number of bytes in the ciphertext block).

### Patches

A patch was released which ensures the HMAC tag is verified before performing CBC decryption. The fixed versions are `>=3.11.4`.

Users should upgrade to `^3.11.4`.

### Credits
Thanks to Morgan Brown of Microsoft for bringing this up and Eva Sarafianou (@esarafianou) for helping to score this advisory.

## References
- https://github.com/panva/jose/security/advisories/GHSA-rvcw-f68w-8h8h
- https://nvd.nist.gov/vuln/detail/CVE-2021-29446
- https://github.com/panva/jose
- https://www.npmjs.com/package/jose-node-cjs-runtime
