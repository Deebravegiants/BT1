# [H] nzo/url-encryptor-bundle Insecure default secret key and IV allowing anyone to decrypt values

## Summary
Severity: High
Advisory: GHSA-r2r8-36pq-27cm
Ecosystem: Packagist
Published: 2024-05-17
Source: https://github.com/advisories/GHSA-r2r8-36pq-27cm
Type: github-advisory

## Affected
- Packagist: `nzo/url-encryptor-bundle` — affected >=5.0.0 <5.0.1
- Packagist: `nzo/url-encryptor-bundle` — affected >=4.0.0 <4.3.2

## Details
Versions of nzo/url-encryptor-bundle prior to 5.0.1 and 4.3.2 are affected by a security vulnerability related to the lack of mandatory key and IV requirements. By default, the bundle uses the aes-256-ctr algorithm, which is susceptible to malleability attacks, potentially leading to Insecure Direct Object Reference (IDOR) vulnerabilities. Additionally, the reuse of keys enables users to decrypt and modify encrypted data if they can guess the plaintext of one ciphertext.

## References
- https://github.com/nayzo/NzoUrlEncryptorBundle/commit/ba3af1a9bcf3bedcc0ed5948979f482e2134da1a
- https://github.com/nayzo/NzoUrlEncryptorBundle/commit/bd8232501c12c9df1bc45b1970870ef665218581
- https://github.com/FriendsOfPHP/security-advisories/blob/master/nzo/url-encryptor-bundle/2020-05-03.yaml
- https://github.com/nayzo/NzoUrlEncryptorBundle
