# [C] morgan-json vulnerable to Arbitrary Code Execution

## Summary
Severity: Critical
Advisory: GHSA-fwv4-6mxc-x5h3
CVE: CVE-2022-25921
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-29
Source: https://github.com/advisories/GHSA-fwv4-6mxc-x5h3
Type: github-advisory

## Affected
- npm: `morgan-json` — affected >=0

## Details
All versions of package morgan-json are vulnerable to Arbitrary Code Execution due to missing sanitization of input passed to the `Function` constructor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25921
- https://github.com/indexzero/morgan-json
- https://github.com/indexzero/morgan-json/blob/3a76010215a4256d41687d082cd66c4f00ea5717/index.js%23L46
- https://security.snyk.io/vuln/SNYK-JS-MORGANJSON-2976193
