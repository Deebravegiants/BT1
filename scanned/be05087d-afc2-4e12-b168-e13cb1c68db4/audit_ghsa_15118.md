# [H] @apollo/experimental-nextjs-app-support Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-rv8p-rr2h-fgpg
CVE: CVE-2024-23841
CWE: CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-rv8p-rr2h-fgpg
Type: github-advisory

## Affected
- npm: `@apollo/experimental-nextjs-app-support` — affected >=0 <0.7.0

## Details
### Impact

The @apollo/experimental-apollo-client-nextjs NPM package is vulnerable to a cross-site scripting vulnerability. This vulnerability arises from improper handling of untrusted input when @apollo/experimental-apollo-client-nextjs performs server-side rendering of HTML pages. To fix this vulnerability, we implemented appropriate escaping to prevent javascript injection into rendered pages.

### Patches

To fix this issue, please update to version 0.7.0 or later.

### Workarounds

There are no known workarounds for this issue. Please update to version 0.7.0

## References
- https://github.com/apollographql/apollo-client-nextjs/security/advisories/GHSA-rv8p-rr2h-fgpg
- https://nvd.nist.gov/vuln/detail/CVE-2024-23841
- https://github.com/apollographql/apollo-client-nextjs/commit/b92bc42abd5f8e17d4db361c36bd08e4f541a46b
- https://github.com/apollographql/apollo-client-nextjs
