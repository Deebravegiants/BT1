# [C] firebase/php-jwt: "None" Algorithm treated as valid on tokens

## Summary
Severity: Critical
Advisory: GHSA-h533-5v22-8vcp
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-h533-5v22-8vcp
Type: github-advisory

## Affected
- Packagist: `firebase/php-jwt` — affected >=0 <2.0.0

## Details
Several widely-used JSON Web Token (JWT) libraries, including node-jsonwebtoken, pyjwt, namshi/jose, php-jwt, and jsjwt, are affected by critical vulnerabilities that could allow attackers to bypass the verification step when using asymmetric keys (RS256, RS384, RS512, ES256, ES384, ES512).

## References
- https://github.com/firebase/php-jwt/commit/b2c2be6a45fda769c8c2ffe5ec4259a9d1e46e5b
- https://auth0.com/blog/2015/03/31/critical-vulnerabilities-in-json-web-token-libraries
- https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries
- https://github.com/FriendsOfPHP/security-advisories/blob/master/firebase/php-jwt/2015-04-02.yaml
- https://github.com/firebase/php-jwt
