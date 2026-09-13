# [M] Symfony's HtmlSanitizer URL Attributes Pass Through BiDi Override Characters → Visual href Spoofing

## Summary
Severity: Medium
Advisory: GHSA-h5vq-qfcg-4m6p
CVE: CVE-2026-45064
CWE: CWE-1007, CWE-451
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-h5vq-qfcg-4m6p
Type: github-advisory

## Affected
- Packagist: `symfony/html-sanitizer` — affected >=6.1.0 <6.4.40
- Packagist: `symfony/html-sanitizer` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/html-sanitizer` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=6.1.0 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

`Symfony\Component\HtmlSanitizer\TextSanitizer\UrlSanitizer::parse()` (used by `UrlSanitizer::sanitize()` and therefore by every `HtmlSanitizer` config that allows links or media) accepts URLs that contain Unicode explicit-direction BiDi formatting characters: U+202A–U+202E (LRE / RLE / PDF / LRO / RLO) and U+2066–U+2069 (LRI / RLI / FSI / PDI). These characters are passed through unchanged into the `href` / `src` attributes produced by `HtmlSanitizer`. When the resulting HTML is rendered in a browser, the override characters reverse or alter the visual ordering of the URL text, so the displayed link can differ arbitrarily from the actual destination: a classic visual-spoofing / phishing primitive against viewers of sanitized content.

### Resolution

`UrlSanitizer::parse()` now rejects URLs containing the explicit-direction BiDi formatting code points (U+202A–U+202E, U+2066–U+2069) before invoking the underlying URL parser. As an unrelated companion fix in the same patch, spaces inside path/query/fragment are now percent-encoded rather than rejected outright, while spaces in the scheme/authority remain rejected by the post-encoding whitespace check.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/743a435e948b897ef2b5564ac438d4beb95d2526) for branch 5.4.

### Credits

Symfony would like to thank Himanshu Anand for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-h5vq-qfcg-4m6p
- https://github.com/symfony/symfony/commit/743a435e948b897ef2b5564ac438d4beb95d2526
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/html-sanitizer/CVE-2026-45064.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45064.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45064
