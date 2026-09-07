# [M] Symfony: HtmlSanitizer UrlAttributeSanitizer Misses URL Attributes

## Summary
Severity: Medium
Advisory: GHSA-x5qj-865h-mgvm
CVE: CVE-2026-48761
CWE: CWE-1023, CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-x5qj-865h-mgvm
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

`Symfony\Component\HtmlSanitizer\Visitor\AttributeSanitizer\UrlAttributeSanitizer::getSupportedAttributes()` enumerates the attribute names whose values are scrubbed through `UrlSanitizer::sanitize()` (scheme and host allow-lists, `javascript:` rejection, BiDi check, etc.). The list is `['src', 'href', 'lowsrc', 'background', 'ping', 'action', 'formaction', 'poster', 'cite']`. Other URL-bearing attributes are absent: `<object data=…>`, `<applet codebase=…>`, `<applet archive=…>` and `<object archive=…>`, `<iframe longdesc=…>` and `<img longdesc=…>`. When an integrator opts these elements/attributes in via `allowElement('object', ['data'])`, `allowElement('applet', ['codebase'])`, etc., or via `allowAttribute()`, no URL sanitization runs: `data="javascript:alert(1)"` and similar payloads ship through unchanged into the output, enabling stored XSS.

`<meta http-equiv="refresh" content="0; url=…">` is the same class of bug routed differently: the URL is embedded inside a multi-field `content` attribute that the per-attribute sanitizer cannot detect from the attribute name alone. Integrators who enable `<meta>` with the `content` attribute (e.g. via `allowStaticElements()`) see `content="0; url=javascript:alert(1)"` pass through, producing a refresh-driven navigation to a `javascript:` URL.

Default configurations are not affected: `<object>`, `<applet>` and `<iframe>` are not in `W3CReference::BODY_ELEMENTS` and `<meta>` requires an explicit opt-in to `<head>` context. The vulnerability surface is integrators who explicitly allow any of those elements together with the listed URL-bearing attributes.

### Resolution

`UrlAttributeSanitizer` now also routes `data`, `codebase`, `archive` and `longdesc` through `UrlSanitizer::sanitize()`. A new `MetaRefreshAttributeSanitizer` registered as a default attribute sanitizer detects the `<delay>; url=<url>` syntax inside `<meta content>`, sanitizes the embedded URL, and drops the attribute if the URL is rejected; non-refresh meta `content` values are passed through unchanged.

The patches for this issue are available [here](https://github.com/symfony/symfony/commit/069a70f9f26e61e9de3b7f9a864a86ed24b36bd0) for branch 6.4 (and forward-ported to 7.4, 8.0 and 8.1).

### Credits

Symfony would like to thank Scott Arciszewski (Trail of Bits) for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-x5qj-865h-mgvm
- https://github.com/symfony/symfony/commit/069a70f9f26e61e9de3b7f9a864a86ed24b36bd0
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/html-sanitizer/CVE-2026-48761.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-48761.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-48761
