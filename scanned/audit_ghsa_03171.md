# [C] Path traversal in rollup-plugin-serve

## Summary
Severity: Critical
Advisory: GHSA-4j46-mp85-mv8c
CVE: CVE-2020-7684
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-4j46-mp85-mv8c
Type: github-advisory

## Affected
- npm: `rollup-plugin-serve` — affected >=0 <1.0.2

## Details
Path traversal in npm package `rollup-plugin-serve` before version 1.0.2. There is no path sanitization in `readFile` operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7684
- https://github.com/thgh/rollup-plugin-serve/commit/3d144f2f47e86fcba34f5a144968da94220e3969
- https://github.com/thgh/rollup-plugin-serve/releases/tag/v1.0.2
- https://vuldb.com/?id.158745
