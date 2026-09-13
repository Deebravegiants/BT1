# [M] Symfony has an HtmlSanitizer allowLinkHosts() / allowMediaHosts() Bypass via URL-Parser Differentials and <area> Misclassification

## Summary
Severity: Medium
Advisory: GHSA-qc95-4862-92fh
CVE: CVE-2026-45066
CWE: CWE-184, CWE-436
Ecosystem: Packagist
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-qc95-4862-92fh
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

`symfony/html-sanitizer` lets applications sanitise untrusted HTML. The configuration methods `allowLinkHosts([...])` and `allowLinkSchemes([...])` are intended to restrict `<a href>` targets to an allowlist of hosts/schemes; `allowMediaHosts()` / `allowMediaSchemes()` do the same for `<img src>` etc.

Three distinct bypasses allow a content author to smuggle off-allowlist URLs past these checks. First, `UrlSanitizer::parse()` parses the input following RFC-3986, while browsers follow the WHATWG URL Standard which normalises `\` to `/` before parsing the authority of "special" schemes; so an input like `https://evil\@trusted.com/` parses with host `trusted.com` server-side but navigates to `https://evil/` in the browser. Second, WHATWG collapses any run of `/` after the scheme into `//`, while RFC-3986 does not; so `https:/evil.com/` and `https:///evil.com/` parse as host-less (skipping the host allowlist) but resolve to `evil.com` in the browser. Third, `UrlAttributeSanitizer` checks `'a' === $element` to route to the link policy and falls through to the media policy otherwise, but `<area>` is a navigable hyperlink equivalent to `<a>`; so `<area href>` was sanitised against the media policy (which typically allows `data:` and may have no host allowlist), bypassing `allowLinkHosts()` / `allowLinkSchemes()` entirely.

### Resolution

`UrlSanitizer::sanitize()` now rejects URLs that contain a backslash or that use a special scheme (`http`, `https`, `ftp`, `ws`, `wss`) followed by a single slash or three slashes before parsing, eliminating the parser-differential bypasses. `UrlAttributeSanitizer` now applies the link policy to both `<a>` and `<area>` elements.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/d506b556d3d3906f3e8660ad82257ce87edbaac4) for branch 5.4.

### Credits

Symfony would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-qc95-4862-92fh
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/html-sanitizer/CVE-2026-45066.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45066.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45066
