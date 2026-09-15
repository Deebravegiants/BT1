# [H] @udecode/plate-link does not sanitize URLs to prevent use of the `javascript:` scheme

## Summary
Severity: High
Advisory: GHSA-4882-hxpr-hrvm
CVE: CVE-2023-34245
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-4882-hxpr-hrvm
Type: github-advisory

## Affected
- npm: `@udecode/plate-link` — affected >=0 <20.0.0

## Details
### Impact
Affected versions of the link plugin and link UI component do not sanitize URLs to prevent use of the `javascript:` scheme. As a result, links with JavaScript URLs can be inserted into the Plate editor through various means, including opening or pasting malicious content.

### Patches
`@udecode/plate-link` 20.0.0 resolves this issue by introducing an `allowedSchemes` option to the link plugin, defaulting to `['http', 'https', 'mailto', 'tel']`. URLs using a scheme that isn't in this list will not be rendered to the DOM.

### Workarounds
If you are unable to update `@udecode/plate-link` to version 20.0.0, we recommend overriding the `LinkElement` and `PlateFloatingLink` components with implementations that explicitly check the URL scheme before rendering any anchor elements.

## References
- https://github.com/udecode/plate/security/advisories/GHSA-4882-hxpr-hrvm
- https://nvd.nist.gov/vuln/detail/CVE-2023-34245
- https://github.com/udecode/plate/pull/2240
- https://github.com/udecode/plate/commit/93dd5712854660874900ae12e4d8e6ff28089eb7
- https://github.com/udecode/plate
