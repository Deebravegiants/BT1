# [M] Symfony: HtmlSanitizer URL Parser Deny Gates Underinclusive: Percent-Encoded BiDi Marks and Unicode Whitespace Bypass Visual-Spoofing Defense

## Summary
Severity: Medium
Advisory: GHSA-v3wm-qf9p-c549
CVE: CVE-2026-48760
CWE: CWE-1007, CWE-451
Ecosystem: Packagist
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-v3wm-qf9p-c549
Type: github-advisory

## Affected
- Packagist: `symfony/html-sanitizer` — affected >=6.1.0 <6.4.41
- Packagist: `symfony/html-sanitizer` — affected >=7.0.0 <7.4.13
- Packagist: `symfony/html-sanitizer` — affected >=8.0.0 <8.0.13
- Packagist: `symfony/symfony` — affected >=6.1.0 <6.4.41
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.13
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.13

## Details
### Description

`Symfony\Component\HtmlSanitizer\TextSanitizer\UrlSanitizer::parse()` rejects URLs containing raw Unicode explicit-direction BiDi formatting characters (U+202A–U+202E, U+2066–U+2069) as a defense against visual-spoofing of the rendered `href`. The check covers only the raw UTF-8 forms of those code points: the percent-encoded forms (`%E2%80%AE` for U+202E, `%E2%81%A6` for U+2066, etc.) are not matched by the deny regex, survive `league/uri`'s parse/build cycle, and are re-emitted unchanged in the sanitized URL. Any downstream consumer that decodes the link before display — phishing-detection filters that compare `urldecode($href)` against a domain allow-list, audit-log dashboards that show a decoded form for readability, hover-tooltip previews, federated/syndicated content where the decoder lives on the consuming side — restores the BiDi character and the visual spoof that the original defense was filed to prevent.

The same `UrlSanitizer::parse()` carries an ASCII-only `/\s/` whitespace check (no `/u` modifier) intended as a backstop against malformed URLs. Without the `/u` modifier, PCRE's `\s` matches only ASCII whitespace, so Unicode whitespace characters — NBSP (U+00A0), the zero-width no-break space / BOM (U+FEFF), line/paragraph separators (U+2028, U+2029), ogham space (U+1680), the U+2000–U+200A en/em quad family, narrow / medium / ideographic spaces (U+202F, U+205F, U+3000) and NEL (U+0085) — pass through unchanged in both raw and percent-encoded forms. In hostname positions they enable lookalike spoofs (`example<NBSP>.com`); in path/query/fragment they enable allow-list drift when a downstream consumer strips whitespace before comparison.

### Resolution

`UrlSanitizer::parse()` now denies BiDi formatting marks together with Unicode whitespace and the zero-width no-break space, in both the raw input and the percent-decoded form of each parsed URL component (`user`, `pass`, `host`, `path`, `query`, `fragment`). ASCII space remains tolerated in path/query/fragment via the existing percent-encoding step.

The patches for this issue are available [here](https://github.com/symfony/symfony/commit/b21a626fd90f5c12d2db432c629eed3e780ba2f8) for branch 6.4 (and forward-ported to 7.4, 8.0 and 8.1).

### Credits

Symfony would like to thank Scott Arciszewski (Trail of Bits) for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-v3wm-qf9p-c549
- https://github.com/symfony/symfony/commit/b21a626fd90f5c12d2db432c629eed3e780ba2f8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/html-sanitizer/CVE-2026-48760.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-48760.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-48760
