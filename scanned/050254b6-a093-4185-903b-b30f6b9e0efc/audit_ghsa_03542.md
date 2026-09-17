# [M] react-dev-utils OS Command Injection in function `getProcessForPort`

## Summary
Severity: Medium
Advisory: GHSA-5q6m-3h65-w53x
CVE: CVE-2021-24033
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-03-11
Source: https://github.com/advisories/GHSA-5q6m-3h65-w53x
Type: github-advisory

## Affected
- npm: `react-dev-utils` — affected >=0.4.0 <11.0.4

## Details
react-dev-utils prior to v11.0.4 exposes a function, `getProcessForPort`, where an input argument is concatenated into a command string to be executed. This function is typically used from react-scripts (in Create React App projects), where the usage is safe. Only when this function is manually invoked with user-provided values (ie: by custom code) is there the potential for command injection. If you're consuming it from react-scripts then this issue does not affect you.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-24033
- https://github.com/facebook/create-react-app/pull/10644
- https://github.com/facebook/create-react-app/commit/f5e415f3a5b66f07dcc60aba1b445fa7cda97268
- https://github.com/facebook/create-react-app
- https://www.facebook.com/security/advisories/cve-2021-24033
- https://www.huntr.dev/bounties/1-npm-react-dev-utils
