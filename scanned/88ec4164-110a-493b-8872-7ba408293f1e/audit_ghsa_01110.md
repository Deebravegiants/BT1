# [M] Cross-Site Scripting in react

## Summary
Severity: Medium
Advisory: GHSA-g53w-52xc-2j85
CVE: CVE-2013-7035
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-g53w-52xc-2j85
Type: github-advisory

## Affected
- npm: `react` — affected >=0.4.0 <0.4.2
- npm: `react` — affected >=0.5.0 <0.5.2

## Details
Affected versions of `react` are vulnerable to Cross-Site Scripting (XSS). The package fails to properly sanitize input used to create keys. This may allow attackers to execute arbitrary JavaScript if a key is generated from user input.


## Recommendation

If you are using `react` 0.5.x, upgrade to version 0.5.2 or later.
If you are using `react` 0.4.x, upgrade to version 0.4.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7035
- https://github.com/facebook/react/commit/393a889aaceb761f058b09a701f889fa8f8b4e64
- https://github.com/facebook/react/commit/94a9a3e752fe089ab23f3a90c26d20d46d62ab10
- https://github.com/facebook/react
- https://reactjs.org/blog/2013/12/18/react-v0.5.2-v0.4.2.html
- https://snyk.io/vuln/npm:react:20131217
