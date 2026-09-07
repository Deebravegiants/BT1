# [M] SVG Injection via Unsanitized Options in @dicebear/core and @dicebear/initials

## Summary
Severity: Medium
Advisory: GHSA-mr9r-mww3-v6gv
CVE: CVE-2026-33311
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-mr9r-mww3-v6gv
Type: github-advisory

## Affected
- npm: `@dicebear/core` — affected >=5.0.0 <5.4.4
- npm: `@dicebear/core` — affected >=6.0.0 <6.1.4
- npm: `@dicebear/core` — affected >=7.0.0 <7.1.4
- npm: `@dicebear/core` — affected >=8.0.0 <8.0.3
- npm: `@dicebear/core` — affected >=9.0.0 <9.4.1
- npm: `@dicebear/initials` — affected >=5.0.0 <5.4.4
- npm: `@dicebear/initials` — affected >=6.0.0 <6.1.4
- npm: `@dicebear/initials` — affected >=7.0.0 <7.1.4
- npm: `@dicebear/initials` — affected >=8.0.0 <8.0.3
- npm: `@dicebear/initials` — affected >=9.0.0 <9.4.1

## Details
## Summary

SVG attribute values derived from user-supplied options (`backgroundColor`, `fontFamily`, `textColor`) were not XML-escaped before interpolation into SVG output. This could allow Cross-Site Scripting (XSS) when applications pass untrusted input to `createAvatar()` and serve the resulting SVG inline or with `Content-Type: image/svg+xml`.

## Affected packages

- **`@dicebear/core`** — `backgroundColor` option values interpolated into SVG attributes without escaping (affects `solid` and `gradientLinear` background types)
- **`@dicebear/initials`** — `fontFamily` and `textColor` option values interpolated into SVG attributes without escaping

## Fix

All affected SVG attribute values are now properly escaped using XML entity encoding. Users should upgrade to the listed patched versions.

## Mitigating factors

- Applications that validate input against the library's JSON Schema before passing it to `createAvatar()` are not affected
- The DiceBear CLI validates input via AJV and was not vulnerable
- Exploitation requires that an application passes untrusted, unvalidated external input directly as option values

## References
- https://github.com/dicebear/dicebear/security/advisories/GHSA-mr9r-mww3-v6gv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33311
- https://github.com/dicebear/dicebear
