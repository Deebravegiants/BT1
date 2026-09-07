# [H] Path Traversal in @finastra/ssr-pages

## Summary
Severity: High
Advisory: GHSA-w6cx-qg2q-rvq8
CVE: CVE-2022-24718
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-w6cx-qg2q-rvq8
Type: github-advisory

## Affected
- npm: `@finastra/ssr-pages` — affected >=0 <0.1.4

## Details
A path traversal issue can occur when providing untrusted input to the `svg` property as an argument to the `build(MessagePageOptions)` function.

### References
- https://github.com/Finastra/ssr-pages/pull/1
- https://github.com/Finastra/ssr-pages/pull/1/commits/c3e4c563384ae3ba3892f37dd190218577620780

## References
- https://github.com/Finastra/ssr-pages/security/advisories/GHSA-w6cx-qg2q-rvq8
- https://nvd.nist.gov/vuln/detail/CVE-2022-24718
- https://github.com/Finastra/ssr-pages/pull/1
- https://github.com/Finastra/ssr-pages/pull/1/commits/c3e4c563384ae3ba3892f37dd190218577620780
- https://github.com/Finastra/ssr-pages
