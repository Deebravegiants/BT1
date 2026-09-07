# [M] Open Redirect in koa-remove-trailing-slashes

## Summary
Severity: Medium
Advisory: GHSA-r773-pmw3-f4mr
CVE: CVE-2021-23384
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-r773-pmw3-f4mr
Type: github-advisory

## Affected
- npm: `koa-remove-trailing-slashes` — affected >=0 <2.0.2

## Details
The package koa-remove-trailing-slashes before 2.0.2 are vulnerable to Open Redirect via the use of trailing double slashes in the URL when accessing the vulnerable endpoint (such as `https://example.com//attacker.example/`). The vulnerable code is in `index.js::removeTrailingSlashes()`, as the web server uses relative URLs instead of absolute URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23384
- https://github.com/vgno/koa-remove-trailing-slashes/commit/e7ce4000e9fe4d957332df1056640a22ebea28ee
- https://github.com/vgno/koa-remove-trailing-slashes
- https://github.com/vgno/koa-remove-trailing-slashes/blame/6a01ba8fd019bd3ece44879c553037ad96ba7d47/index.js#L31
- https://snyk.io/vuln/SNYK-JS-KOAREMOVETRAILINGSLASHES-1085708
