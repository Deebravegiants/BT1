# [H] HTML Injection in marky-markdown

## Summary
Severity: High
Advisory: GHSA-mg69-6j3m-jvgw
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-mg69-6j3m-jvgw
Type: github-advisory

## Affected
- npm: `marky-markdown` — affected >=0.0.0

## Details
All versions of `marky-markdown` are vulnerable to HTML Injection. The package fails to sanitize `style` attributes in `img` tags of the markdown input. This may allow attackers to affect the size of images in the rendered HTML.


## Recommendation

This package is no longer maintained. Please upgrade to `@npmcorp/marky-markdown`

## References
- https://github.com/npm/marky-markdown
- https://snyk.io/vuln/SNYK-JS-MARKYMARKDOWN-548871
- https://www.npmjs.com/advisories/1470
