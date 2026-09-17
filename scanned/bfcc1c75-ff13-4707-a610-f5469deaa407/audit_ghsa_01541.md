# [H] Directory traversal in rollup-plugin-server

## Summary
Severity: High
Advisory: GHSA-34gh-3cwv-wvp2
CVE: CVE-2020-7683
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-34gh-3cwv-wvp2
Type: github-advisory

## Affected
- npm: `rollup-plugin-server` — affected >=0

## Details
This affects all versions of package rollup-plugin-server. There is no path sanitization in readFile operation performed inside the readFileFromContentBase function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7683
- https://snyk.io/vuln/SNYK-JS-ROLLUPPLUGINSERVER-590123
