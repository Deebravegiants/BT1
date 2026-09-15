# [C] curlrequest allows execution of arbitrary commands

## Summary
Severity: Critical
Advisory: GHSA-m8xj-5v73-3hh8
CVE: CVE-2020-7646
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-13
Source: https://github.com/advisories/GHSA-m8xj-5v73-3hh8
Type: github-advisory

## Affected
- npm: `curlrequest` — affected >=0

## Details
curlrequest through 1.0.1 allows execution of arbitrary commands. It is possible to inject arbitrary commands by using a semicolon char in any of the `options` values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7646
- https://github.com/node-js-libs/curlrequest
- https://github.com/node-js-libs/curlrequest/blob/master/index.js#L239
- https://snyk.io/vuln/SNYK-JS-CURLREQUEST-568274
