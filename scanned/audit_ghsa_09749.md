# [H] @vitejs/plugin-rsc has a Denial of Service with React Server Components

## Summary
Severity: High
Advisory: GHSA-v457-wxvj-p9w9
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-v457-wxvj-p9w9
Type: github-advisory

## Affected
- npm: `@vitejs/plugin-rsc` — affected >=0 <0.5.23

## Details
### Impact

`@vitejs/plugin-rsc` vendors `react-server-dom-webpack`, which contained a vulnerability in versions prior to 19.2.4. See details in React repository's advisory https://github.com/facebook/react/security/advisories/GHSA-479c-33wc-g2pg

### Patches

Upgrade immediately to `@vitejs/plugin-rsc@0.5.23` or later.

## References
- https://github.com/vitejs/vite-plugin-react/security/advisories/GHSA-v457-wxvj-p9w9
- https://github.com/vitejs/vite-plugin-react
