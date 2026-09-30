# [H] Symfony's HEAD Request Bypasses methods: ['GET'] Filter in #[IsGranted] / #[IsSignatureValid] / #[IsCsrfTokenValid]

## Summary
Severity: High
Advisory: GHSA-6439-2f28-8p8q
CVE: CVE-2026-45075
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-6439-2f28-8p8q
Type: github-advisory

## Affected
- Packagist: `symfony/http-kernel` — affected >=7.4.0 <7.4.12
- Packagist: `symfony/http-kernel` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/security-http` — affected >=7.4.0 <7.4.12
- Packagist: `symfony/security-http` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=7.4.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

Symfony's `#[IsGranted('...')]`, `#[IsSignatureValid]`, and `#[IsCsrfTokenValid(...)]` attributes allow you to define a `methods: [...]` argument to only enforce these checks for the listed HTTP methods and skip them otherwise. E.g. an attribute defining `methods: ['GET']` would be ignored for a `HEAD` request.

On the other hand, Symfony's router (and HTTP semantics generally) serves `HEAD` requests using the `GET` handler. Therefore, a controller protected by e.g. `#[IsGranted('ROLE_ADMIN', methods: ['GET'])]` can be reached via `HEAD` with the authorization check silently skipped.

Even if the `HEAD` request won't get any response content, response headers leak (`Content-Length`, `Location`, custom headers). Also, the controller still executes and any side effects (DB writes, state changes) occur.

### Resolution

When adding `GET` in the `methods` option of these attributes, Symfony now also include the `HEAD` method automatically.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/fa8d5c67aa4b22c9656e3fd7d5c3aa59865bf838) for branch 7.4.

### Credits

Symfony would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and Alexandre Daubois for fixing it.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-6439-2f28-8p8q
- https://github.com/symfony/symfony/commit/fa8d5c67aa4b22c9656e3fd7d5c3aa59865bf838
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-kernel/CVE-2026-45075.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2026-45075.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45075.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45075
