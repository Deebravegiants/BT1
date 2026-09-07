# [M] repostat: Reflected Cross-Site Scripting (XSS) via repo prop in RepoCard

## Summary
Severity: Medium
Advisory: GHSA-fm8c-6m29-rp6j
CVE: CVE-2026-27612
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-fm8c-6m29-rp6j
Type: github-advisory

## Affected
- npm: `repostat` — affected >=0 <1.0.1

## Details
### Impact
The `RepoCard` component is vulnerable to Reflected Cross-Site Scripting (XSS). The vulnerability occurs because the component uses React's `dangerouslySetInnerHTML` to render the repository name (`repo` prop) during the loading state without any sanitization. 

If a developer using this package passes unvalidated user input directly into the `repo` prop (for example, reading it from a URL query parameter), an attacker can execute arbitrary JavaScript in the context of the user's browser.

### Proof of Concept
```jsx
import { RepoCard } from 'repostat';

function App() {
  const params = new URLSearchParams(window.location.search);
  const maliciousRepo = params.get('repo') || 'facebook/react';

  return <RepoCard repo={maliciousRepo} token="YOUR_TOKEN" />;
}
```

### Remediation
Update to version 1.0.1. The use of dangerouslySetInnerHTML has been removed, and the repo prop is now safely rendered using standard React JSX data binding, which automatically escapes HTML entities.

## References
- https://github.com/denpiligrim/repostat/security/advisories/GHSA-fm8c-6m29-rp6j
- https://nvd.nist.gov/vuln/detail/CVE-2026-27612
- https://github.com/denpiligrim/repostat/commit/715df5f73359d222fd7876e948d14290180e3c88
- https://github.com/denpiligrim/repostat
