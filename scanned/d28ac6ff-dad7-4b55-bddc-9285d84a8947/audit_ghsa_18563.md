# [C] docusaurus-plugin-content-gists vulnerability exposes GitHub Personal Access Token

## Summary
Severity: Critical
Advisory: GHSA-qf34-qpr4-5pph
CVE: CVE-2025-53624
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-qf34-qpr4-5pph
Type: github-advisory

## Affected
- npm: `docusaurus-plugin-content-gists` — affected >=0 <4.0.0

## Details
## GitHub Personal Access Token Exposure in docusaurus-plugin-content-gists

### Summary

docusaurus-plugin-content-gists versions prior to 4.0.0 are vulnerable to exposing GitHub Personal Access Tokens in production build artifacts when passed through plugin configuration options. The token, intended for build-time API access only, is inadvertently included in client-side JavaScript bundles, making it accessible to anyone who can view the website's source code.

### Affected Versions

- All versions < 4.0.0

### Patched Versions

- Version 4.0.0 and later

### Impact

When using the affected versions with the recommended configuration pattern:

```javascript
plugins: [
  [
    'docusaurus-plugin-content-gists',
    {
      personalAccessToken: process.env.GITHUB_PERSONAL_ACCESS_TOKEN,
    },
  ],
]
```

The GitHub Personal Access Token is included in the webpack bundle and exposed in production builds at:
- `/build/assets/js/main.[hash].js`

This allows malicious actors to:
- Extract the GitHub Personal Access Token from the website's JavaScript files
- Use the stolen token to access the token owner's GitHub account with the granted permissions
- Potentially access private gists, repositories, or perform other actions depending on the token's scope

## Mitigation steps

  1. Immediately revoke access to the GitHub PAT that was used: https://github.com/settings/tokens

### Migration steps

  1. Update to version 4.0.0+: `npm install docusaurus-plugin-content-gists@^4.0.0`
  3. Remove `personalAccessToken` from your plugin configuration
  4. Ensure `GH_PERSONAL_ACCESS_TOKEN` is set in your build environment

## References
- https://github.com/webbertakken/docusaurus-plugin-content-gists/security/advisories/GHSA-qf34-qpr4-5pph
- https://nvd.nist.gov/vuln/detail/CVE-2025-53624
- https://github.com/webbertakken/docusaurus-plugin-content-gists/commit/8d4230b82412edb215ddfa9e609d178510a5fe31
- https://github.com/webbertakken/docusaurus-plugin-content-gists
