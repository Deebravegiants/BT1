# [H] react-dev-utils on Windows vulnerable to Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-29gp-92wp-94q8
CVE: CVE-2018-6342
CWE: CWE-78
Ecosystem: npm
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-29gp-92wp-94q8
Type: github-advisory

## Affected
- npm: `react-dev-utils` — affected >=1.0.0 <1.0.4
- npm: `react-dev-utils` — affected >=2.0.0 <2.0.2
- npm: `react-dev-utils` — affected >=3.0.0 <3.1.2
- npm: `react-dev-utils` — affected >=4.0.0 <4.2.2
- npm: `react-dev-utils` — affected >=5.0.0 <5.0.2

## Details
`react-dev-utils` on Windows is vulnerable to remote code execution.


## Recommendation

Update to one of the following versions, depending on the release line that you are using.
- 1.0.4
- 2.0.2
- 3.1.2
- 4.2.2
- 5.0.2
- 6.0.0-next.a671462c

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6342
- https://github.com/facebook/create-react-app/pull/4866
- https://github.com/advisories/GHSA-29gp-92wp-94q8
- https://github.com/facebook/create-react-app
- https://github.com/facebook/create-react-app/releases/tag/v1.1.5
- https://www.npmjs.com/advisories/695
