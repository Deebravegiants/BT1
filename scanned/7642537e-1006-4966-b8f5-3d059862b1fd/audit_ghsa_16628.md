# [M] asymmetricrypt/asymmetricrypt Padding Oracle Vulnerability in RSA Encryption

## Summary
Severity: Medium
Advisory: GHSA-87mp-xc4x-x8rh
CWE: CWE-327
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-87mp-xc4x-x8rh
Type: github-advisory

## Affected
- Packagist: `asymmetricrypt/asymmetricrypt` — affected >=0

## Details
The encryption and decryption process were vulnerable against the Bleichenbacher's attack, which is a padding oracle vulnerability disclosed in the 98'.
The issue was about the wrong padding utilized, which allowed to retrieve the encrypted content.
The OPENSSL_PKCS1_PADDING version, aka PKCS v1.5 was vulnerable (is the one set by default when using openssl_* methods), while the PKCS v2.0 isn't anymore (it's also called OAEP).

A fix for this vulnerability was merged at https://github.com/Cosmicist/AsymmetriCrypt/pull/5/commits/a0318cfc5022f2a7715322dba3ff91d475ace7c6.

## References
- https://github.com/Cosmicist/AsymmetriCrypt/issues/4
- https://github.com/Cosmicist/AsymmetriCrypt/pull/5
- https://github.com/Cosmicist/AsymmetriCrypt
- https://github.com/FriendsOfPHP/security-advisories/blob/master/asymmetricrypt/asymmetricrypt/2017-11-20.yaml
