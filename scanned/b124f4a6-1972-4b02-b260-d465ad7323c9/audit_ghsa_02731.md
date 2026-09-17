# [H] Regular expression denial of service in react-native

## Summary
Severity: High
Advisory: GHSA-7f53-fmmv-mfjv
CVE: CVE-2020-1920
CWE: CWE-400, CWE-697
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-07-20
Source: https://github.com/advisories/GHSA-7f53-fmmv-mfjv
Type: github-advisory

## Affected
- npm: `react-native` — affected >=0.59.0 <0.62.3
- npm: `react-native` — affected >=0.63.0 <0.64.1

## Details
A regular expression denial of service (ReDoS) vulnerability in the validateBaseUrl function can cause the application to use excessive resources, become unresponsive, or crash. This was introduced in react-native version 0.59.0 and fixed in version 0.64.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1920
- https://github.com/facebook/react-native/commit/ca09ae82715e33c9ac77b3fa55495cf84ba891c7
- https://github.com/facebook/react-native/releases/tag/v0.62.3
- https://github.com/facebook/react-native/releases/tag/v0.64.1
- https://securitylab.github.com/advisories/GHSL-2020-293-redos-react-native
- https://www.npmjs.com/package/react-native
