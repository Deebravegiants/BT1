# [M] Cross Site Scripting (XSS) in @finastra/ssr-pages

## Summary
Severity: Medium
Advisory: GHSA-7f63-h6g3-7cwm
CVE: CVE-2022-24717
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-7f63-h6g3-7cwm
Type: github-advisory

## Affected
- npm: `@finastra/ssr-pages` — affected >=0 <0.1.5

## Details
A cross site scripting (XSS) issue can occur when providing untrusted input to the `redirect.link` property as an argument to the `build(MessagePageOptions)` function.

### References
- https://github.com/Finastra/ssr-pages/pull/2
- https://github.com/Finastra/ssr-pages/pull/2/commits/133606ffaec2edd9918d9fba5771ed21da7876a5
- https://github.com/Finastra/ssr-pages/commit/98abc59e28fec48246be0d59ac144675d6361073

## References
- https://github.com/Finastra/ssr-pages/security/advisories/GHSA-7f63-h6g3-7cwm
- https://nvd.nist.gov/vuln/detail/CVE-2022-24717
- https://github.com/Finastra/ssr-pages/pull/2
- https://github.com/Finastra/ssr-pages/pull/2/commits/133606ffaec2edd9918d9fba5771ed21da7876a5
- https://github.com/Finastra/ssr-pages/commit/98abc59e28fec48246be0d59ac144675d6361073
- https://github.com/Finastra/ssr-pages
