# [M] Prototype Pollution in dotty

## Summary
Severity: Medium
Advisory: GHSA-6g47-63mv-qpgh
CVE: CVE-2021-23624
CWE: CWE-1321, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-6g47-63mv-qpgh
Type: github-advisory

## Affected
- npm: `dotty` — affected >=0 <0.1.2

## Details
This affects the package dotty before 0.1.2. A type confusion vulnerability can lead to a bypass of CVE-2021-25912 when the user-provided keys used in the path parameter are arrays.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23624
- https://github.com/deoxxa/dotty/commit/88f61860dcc274a07a263c32cbe9d44c24ef02d7
- https://github.com/deoxxa/dotty
- https://snyk.io/vuln/SNYK-JS-DOTTY-1577292
