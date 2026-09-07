# [H] Prototype pollution vulnerability found in Mermaid's bundled version of DOMPurify

## Summary
Severity: High
Advisory: GHSA-m4gq-x24j-jpmf
CWE: CWE-1321, CWE-1395
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2024-10-22
Source: https://github.com/advisories/GHSA-m4gq-x24j-jpmf
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=0 <10.9.3

## Details
The following bundled files within the Mermaid NPM package contain a bundled version of DOMPurify that is vulnerable to https://github.com/cure53/DOMPurify/security/advisories/GHSA-mmhx-hmjr-r674, potentially resulting in an XSS attack.

This affects the built:

- `dist/mermaid.min.js`
- `dist/mermaid.js`
- `dist/mermaid.esm.mjs`
- `dist/mermaid.esm.min.mjs`

This will also affect users that use the above files via a CDN link, e.g. `https://cdn.jsdelivr.net/npm/mermaid@10.9.2/dist/mermaid.min.js`

**Users that use the default NPM export of `mermaid`, e.g. `import mermaid from 'mermaid'`, or the `dist/mermaid.core.mjs` file, do not use this bundled version of DOMPurify, and can easily update using their package manager with something like `npm audit fix`.**

### Patches

- `develop` branch: 6c785c93166c151d27d328ddf68a13d9d65adc00
- backport to v10: 92a07ffe40aab2769dd1c3431b4eb5beac282b34

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-mmhx-hmjr-r674
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-m4gq-x24j-jpmf
- https://github.com/mermaid-js/mermaid/commit/6c785c93166c151d27d328ddf68a13d9d65adc00
- https://github.com/mermaid-js/mermaid/commit/92a07ffe40aab2769dd1c3431b4eb5beac282b34
- https://github.com/mermaid-js/mermaid
