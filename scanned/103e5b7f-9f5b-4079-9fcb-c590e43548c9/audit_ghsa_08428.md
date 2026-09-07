# [M] Symfony has a UrlGenerator Route-Requirement Bypass via Unanchored Regex Alternation → Off-Site //host URL Injection

## Summary
Severity: Medium
Advisory: GHSA-72xp-p242-47p9
CVE: CVE-2026-45065
CWE: CWE-185, CWE-601
Ecosystem: Packagist
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-72xp-p242-47p9
Type: github-advisory

## Affected
- Packagist: `symfony/routing` — affected >=0 <5.4.52
- Packagist: `symfony/routing` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/routing` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/routing` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=0 <5.4.52
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

Symfony routes can declare a requirements regex per path parameter, e.g. a route `/{_locale}/blog` with `requirements: { _locale: 'en|fr|de' }`. The Twig `path()` / `url()` helpers (backed by `UrlGenerator`) validate supplied parameter values against that regex before building the URL.

UrlGenerator constructs the validation pattern as `'#^'.$req.'$#'`, where `$req` is the raw requirement string. For a requirement expressed as an alternation, e.g. `_locale: 'ar|bg|...|vi|...|zh_CN'` (very common), `^` and `$` anchor only the first and last alternatives, so any middle alternative matches as an unanchored substring. A value like `/evil.com` satisfies the requirement (because it contains `vi`), and the generated path becomes `//evil.com/...`: a protocol-relative URL the browser navigates off-site.

### Resolution

The `UrlGenerator` class now wraps the requirement in a non-capturing group so the `^` and `$` anchors apply to the whole alternation.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/bcf487c22f3240ba994124e0e0fe8616f3cfc47a) for branch 5.4.

### Credits

Symfony would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-72xp-p242-47p9
- https://github.com/symfony/symfony/commit/bcf487c22f3240ba994124e0e0fe8616f3cfc47a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/routing/CVE-2026-45065.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45065.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45065
