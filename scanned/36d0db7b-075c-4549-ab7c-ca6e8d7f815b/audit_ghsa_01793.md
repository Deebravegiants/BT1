# [H] ReDOS in IS-SVG

## Summary
Severity: High
Advisory: GHSA-r8j5-h5cx-65gg
CVE: CVE-2021-29059
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-r8j5-h5cx-65gg
Type: github-advisory

## Affected
- npm: `is-svg` — affected >=2.1.0 <4.3.0

## Details
A vulnerability was discovered in IS-SVG version 4.3.1 and below where a Regular Expression Denial of Service (ReDOS) occurs if the application is provided and checks a crafted invalid SVG string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29059
- https://github.com/sindresorhus/is-svg/commit/732fc72779840c45a30817d3fe28e12058592b02
- https://github.com/sindresorhus/is-svg
- https://github.com/sindresorhus/is-svg/releases/tag/v4.3.0
- https://github.com/yetingli/PoCs/blob/main/CVE-2021-29059/IS-SVG.md
- https://github.com/yetingli/SaveResults/blob/main/js/is-svg.js
- https://www.npmjs.com/package/is-svg
