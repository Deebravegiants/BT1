# [H] namshi/jose insecure JSON Web Signatures (JWS)

## Summary
Severity: High
Advisory: GHSA-hxhc-wmg8-xrqf
Ecosystem: Packagist
Published: 2024-05-17
Source: https://github.com/advisories/GHSA-hxhc-wmg8-xrqf
Type: github-advisory

## Affected
- Packagist: `namshi/jose` — affected >=0 <1.1.2
- Packagist: `namshi/jose` — affected >=1.2.0 <1.2.2
- Packagist: `namshi/jose` — affected >=2.0.0 <2.0.3
- Packagist: `namshi/jose` — affected >=2.1.0 <2.1.2

## Details
namshi/jose allows the acceptance of unsecure JSON Web Signatures (JWS) by default. The vulnerability arises from the $allowUnsecure flag, which, when set to true during the loading of JWSes, permits tokens signed with 'none' algorithms to be processed. This behavior poses a significant security risk as it could allow an attacker to impersonate users by crafting a valid jwt token.

## References
- https://github.com/namshi/jose/commit/009f86d6ced000b806b2f602c0b7393060ebb34e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/namshi/jose/2015-02-19.yaml
- https://github.com/namshi/jose
