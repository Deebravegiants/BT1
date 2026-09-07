# [M] CommonMark has DisallowedRawHtml extension bypass via whitespace in HTML tag names

## Summary
Severity: Medium
Advisory: GHSA-4v6x-c7xx-hw9f
CVE: CVE-2026-30838
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-4v6x-c7xx-hw9f
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=2.0.0 <2.8.1

## Details
### Impact

The `DisallowedRawHtml` extension can be bypassed by inserting a newline, tab, or other ASCII whitespace character between a disallowed HTML tag name and the closing `>`. For example, `<script\n>` would pass through unfiltered and be rendered as a valid HTML tag by browsers. This is a cross-site scripting (XSS) vector for any application that relies on this extension to sanitize untrusted user input.

All applications using the `DisallowedRawHtml` extension to process untrusted markdown are affected. Applications that use a dedicated HTML sanitizer (such as HTML Purifier) on the rendered output are not affected.

### Patches

Fixed in 2.8.1. The regex character class `[ \/>]` was changed to `[\s\/>]` to match all whitespace characters that browsers accept as valid tag name terminators.

### Workarounds

- Set the `html_input` configuration option to `'escape'` or `'strip'` to disable all raw HTML, though this is a broader restriction than the `DisallowedRawHtml` extension provides.
- Pass the rendered HTML through a dedicated HTML sanitizer before serving it to users ([always recommended](https://commonmark.thephpleague.com/2.x/security/#additional-filtering))

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-4v6x-c7xx-hw9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-30838
- https://commonmark.thephpleague.com/extensions/disallowed-raw-html
- https://github.com/thephpleague/commonmark
