# [H] sjcl is missing point-on-curve validation in sjcl.ecc.basicKey.publicKey

## Summary
Severity: High
Advisory: GHSA-2w8x-224x-785m
CVE: CVE-2026-4258
CWE: CWE-325, CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-2w8x-224x-785m
Type: github-advisory

## Affected
- npm: `sjcl` — affected >=0 <1.0.9

## Details
All versions of the package sjcl are vulnerable to Improper Verification of Cryptographic Signature due to missing point-on-curve validation in sjcl.ecc.basicKey.publicKey(). An attacker can recover a victim's ECDH private key by sending crafted off-curve public keys and observing ECDH outputs. The dhJavaEc() function directly returns the raw x-coordinate of the scalar multiplication result (no hashing), providing a plaintext oracle without requiring any decryption feedback.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4258
- https://github.com/bitwiseshiftleft/sjcl/commit/ee307459972442a17beebc29dc331fffd8aff796
- https://gist.github.com/Kr0emer/2560f98edb10b0b34f2438cd63913c47
- https://github.com/bitwiseshiftleft/sjcl
- https://github.com/bitwiseshiftleft/sjcl/blob/master/core/ecc.js#L454-L461
- https://security.snyk.io/vuln/SNYK-JS-SJCL-15369617
