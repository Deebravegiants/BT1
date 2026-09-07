# [M] justhtml includes multiple security fixes

## Summary
Severity: Medium
Advisory: GHSA-c9vm-hv86-f23r
CWE: CWE-178, CWE-20, CWE-755, CWE-79
Ecosystem: PyPI
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-c9vm-hv86-f23r
Type: github-advisory

## Affected
- PyPI: `justhtml` — affected >=0 <1.15.0

## Details
## Summary

`justhtml` `1.15.0` includes multiple security fixes affecting URL sanitization helpers, HTML serialization, Markdown passthrough, and several custom sanitization-policy edge cases.

These issues have different impact levels and do not all affect the default configuration in the same way.

## Affected versions

- `justhtml` `<= 1.14.0`

## Fixed version

- `justhtml` `1.15.0` released on April 9, 2026

## Impact overview

### Helper and serialization issues
These issues could affect applications using JustHTML helpers or programmatic DOM construction, even outside the default HTML sanitization path.

- `JustHTML.clean_url_value(...)` and `clean_url_in_js_string(...)` could accept URL values such as `javascript&#58...`, which became active `javascript:` URLs after HTML attribute parsing.
- URL sanitization could treat values like `\\evil.example/x` or `/\\evil.example/x` as safe relative URLs even though browsers could resolve them as remote requests.
- Malformed bracketed hosts such as `https://[evil.example]/x` could raise exceptions and crash sanitization when host allowlists were used.
- Programmatic element or attribute names containing markup-breaking characters could be serialized into active HTML.
- Programmatic HTML comments containing `-->` could break out of the comment and inject live markup.

### Markdown passthrough issue
- `to_markdown(html_passthrough=True)` could reintroduce active HTML from sanitized `<textarea>` content by emitting a raw closing `</textarea>` sequence.

### Custom policy issues
These issues affected custom policies more than the default safe configuration.

- `a[ping]` was handled as a single URL even though browsers interpret it as a space-separated URL list.
- `attributionsrc` was not treated as URL-bearing and could preserve attacker-controlled reporting endpoints.
- `link[imagesrcset]` was not treated as URL-bearing and could preserve attacker-controlled image candidates.
- Preserved `<meta http-equiv="refresh">` tags could keep redirect targets without URL-policy enforcement.
- Preserved `<base href>` tags could rewrite how later relative URLs resolved in the browser.
- Preserved `<style>` blocks could keep resource-loading CSS such as `@import`, `url(...)`, or `image-set(...)`.
- Mixed-case attribute names in custom transform pipelines could bypass or confuse security-related transforms such as `DropAttrs(...)`, `DropUrlAttrs(...)`, `AllowStyleAttrs(...)`, and `MergeAttrs(...)`.

## Default configuration

Most of the custom-policy issues above did **not** affect the default `JustHTML(..., sanitize=True)` behavior.

The main exceptions were:
- helper APIs such as `clean_url_value(...)`
- programmatic DOM / serializer usage
- applications explicitly using `html_passthrough=True`
- applications using custom policies or custom transform pipelines

## Recommended action

Upgrade to `justhtml` `1.15.0`.

If you cannot upgrade immediately:

- avoid `html_passthrough=True` for untrusted content
- avoid preserving `<style>`, `<meta http-equiv="refresh">`, and `<base href>` in custom policies
- avoid allowing `ping`, `attributionsrc`, or `imagesrcset` unless you explicitly validate them
- avoid serializing untrusted programmatic node names, attribute names, or comment data

## References
- https://github.com/EmilStenstrom/justhtml/security/advisories/GHSA-c9vm-hv86-f23r
- https://github.com/EmilStenstrom/justhtml
- https://github.com/EmilStenstrom/justhtml/compare/v1.14.0...v1.15.0
- https://github.com/EmilStenstrom/justhtml/releases/tag/v1.15.0
