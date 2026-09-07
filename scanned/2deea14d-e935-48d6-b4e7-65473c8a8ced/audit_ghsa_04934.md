# [M] TinaCMS rich-text (slatejson) rendering does not sanitize link/image URLs, allowing stored XSS via dangerous URL schemes

## Summary
Severity: Medium
Advisory: GHSA-2vcc-5v34-9jc8
CVE: CVE-2026-55661
CWE: CWE-79, CWE-87
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-2vcc-5v34-9jc8
Type: github-advisory

## Affected
- npm: `tinacms` — affected >=0 <3.9.3
- npm: `@tinacms/mdx` — affected >=0 <2.1.7

## Details
TinaCMS rich-text parsing and the default link/image renderers did not sanitize the `url` field on Slate link/image nodes. Content containing `javascript:` or `data:text/html` URLs — including case-variant, whitespace-padded, and control-character-obfuscated forms — is rendered into `href`/`src` and executes when the content is viewed. Any actor able to author rich-text content (for example a lower-privileged editor, or imported/external content) can achieve stored XSS against editors and site viewers.

Fixed in https://github.com/tinacms/tinacms/pull/7056 via a `sanitizeUrl()` helper (case-insensitive, whitespace/control-character-normalized scheme allow-list) applied recursively to Slate trees at parse time and in the default rich-text rendering.

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-2vcc-5v34-9jc8
- https://github.com/tinacms/tinacms/pull/7056
- https://github.com/tinacms/tinacms
