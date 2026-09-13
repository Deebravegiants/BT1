# [M] Symfony's OidcTokenHandler Accepts JWTs Missing aud/iss/exp Claims

## Summary
Severity: Medium
Advisory: GHSA-29fc-p6c4-24cg
CVE: CVE-2026-45069
CWE: CWE-1287, CWE-345
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-29fc-p6c4-24cg
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=6.3.0 <6.4.40
- Packagist: `symfony/security-http` — affected >=7.4.0 <7.4.12
- Packagist: `symfony/security-http` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=6.3.0 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.4.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

`OidcTokenHandler` is Symfony's built-in access-token handler for OpenID Connect: it validates a bearer JWT and returns the authenticated user identity. It delegates claim validation to the `web-token/jwt-checker` library's `ClaimCheckerManager`.

`OidcTokenHandler::verifyClaims()` registers audience (`aud`), issuer (`iss`), and expiry (`exp`) checkers, but never passes the `$mandatoryClaims` argument to `ClaimCheckerManager::check()`. That method only validates claims that are *present* in the token: a checker for an absent claim is silently skipped. A validly-signed JWT that simply **omits** `aud`, `iss`, and `exp` therefore passes verification.

### Resolution

The `OidcTokenHandler` now calls the `ClaimCheckerManager` with the list of mandatory claims so that tokens missing `aud`, `iss`, or `exp` are rejected.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/6b717aaac21b7e96798448d14c4355ea87690b3d) for branch 6.4.

### Credits

Symfony would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-29fc-p6c4-24cg
- https://github.com/symfony/symfony/commit/6b717aaac21b7e96798448d14c4355ea87690b3d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2026-45069.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45069.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45069
