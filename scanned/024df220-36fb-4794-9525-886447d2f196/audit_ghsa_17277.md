# [M] Vite Plugin React has a Source Code Exposure Vulnerability in React Server Components

## Summary
Severity: Medium
Advisory: GHSA-c6m7-q6pr-c64r
CWE: CWE-1395, CWE-497, CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-c6m7-q6pr-c64r
Type: github-advisory

## Affected
- npm: `@vitejs/plugin-rsc` — affected >=0 <0.5.7

## Details
### Impact

`@vitejs/plugin-rsc` vendors `react-server-dom-webpack`, which contained a vulnerability in versions prior to 19.2.3. See details in React repository's advisory https://github.com/facebook/react/security/advisories/GHSA-925w-6v3x-g4j4

### Patches

Upgrade immediately to `@vitejs/plugin-rsc@0.5.7` or later.

## References
- https://github.com/facebook/react/security/advisories/GHSA-925w-6v3x-g4j4
- https://github.com/vitejs/vite-plugin-react/security/advisories/GHSA-c6m7-q6pr-c64r
- https://github.com/vitejs/vite-plugin-react
