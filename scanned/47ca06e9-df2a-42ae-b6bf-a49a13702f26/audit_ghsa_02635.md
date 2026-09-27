# [M] File reference keys leads to incorrect hashes on HMAC algorithms

## Summary
Severity: Medium
Advisory: GHSA-7322-jrq4-x5hf
CVE: CVE-2021-41106
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-29
Source: https://github.com/advisories/GHSA-7322-jrq4-x5hf
Type: github-advisory

## Affected
- Packagist: `lcobucci/jwt` — affected >=3.4.0 <3.4.6
- Packagist: `lcobucci/jwt` — affected >=4.0.0 <4.0.4
- Packagist: `lcobucci/jwt` — affected >=4.1.0 <4.1.5

## Details
### Impact

Users of HMAC-based algorithms (HS256, HS384, and HS512) combined with `Lcobucci\JWT\Signer\Key\LocalFileReference` as key are having their tokens issued/validated using the file path as hashing key - instead of the contents.

The HMAC hashing functions take any string as input and, since users can issue and validate tokens, people are lead to believe that everything works properly.

### Patches

All versions have been patched to always load the file contents, deprecated the `Lcobucci\JWT\Signer\Key\LocalFileReference`, and suggest `Lcobucci\JWT\Signer\Key\InMemory` as the alternative.

### Workarounds

Use `Lcobucci\JWT\Signer\Key\InMemory` instead of `Lcobucci\JWT\Signer\Key\LocalFileReference` to create the instances of your keys:

```diff
-use Lcobucci\JWT\Signer\Key\LocalFileReference;
+use Lcobucci\JWT\Signer\Key\InMemory;

-$key = LocalFileReference::file(__DIR__ . '/public-key.pem');
+$key = InMemory::file(__DIR__ . '/public-key.pem');
```

## References
- https://github.com/lcobucci/jwt/security/advisories/GHSA-7322-jrq4-x5hf
- https://nvd.nist.gov/vuln/detail/CVE-2021-41106
- https://github.com/lcobucci/jwt/commit/8175de5b841fbe3fd97d2d49b3fc15c4ecb39a73
- https://github.com/lcobucci/jwt/commit/c45bb8b961a8e742d8f6b88ef5ff1bd5cca5d01c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/lcobucci/jwt/CVE-2021-41106.yaml
- https://github.com/lcobucci/jwt
