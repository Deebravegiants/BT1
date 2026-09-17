# [M] CVE-2021-29445

## Summary
Severity: Medium
Advisory: CVE-2021-29445
Aliases: GHSA-4v4g-726h-xvfv
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-16
Source: https://osv.dev/vulnerability/CVE-2021-29445
Type: osv

## Details
jose-node-esm-runtime is an npm package which provides a number of cryptographic functions. In versions prior to 3.11.4 the AES_CBC_HMAC_SHA2 Algorithm (A128CBC-HS256, A192CBC-HS384, A256CBC-HS512) decryption would always execute both HMAC tag verification and CBC decryption, if either failed `JWEDecryptionFailed` would be thrown. But a possibly observable difference in timing when padding error would occur while decrypting the ciphertext makes a padding oracle and an adversary might be able to make use of that oracle to decrypt data without knowing the decryption key by issuing on average 128*b calls to the padding oracle (where b is the number of bytes in the ciphertext block). A patch was released which ensures the HMAC tag is verified before performing CBC decryption. The fixed versions are `>=3.11.4`. Users should upgrade to `^3.11.4`.

## References
- https://github.com/panva/jose/security/advisories/GHSA-4v4g-726h-xvfv
- https://www.npmjs.com/package/jose-node-esm-runtime
