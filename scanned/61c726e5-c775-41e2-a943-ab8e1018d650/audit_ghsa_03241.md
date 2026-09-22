# [C] OS Command Injection in closure-compiler-stream

## Summary
Severity: Critical
Advisory: GHSA-m647-5wf9-3jp3
CVE: CVE-2020-7603
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-m647-5wf9-3jp3
Type: github-advisory

## Affected
- npm: `closure-compiler-stream` — affected >=0

## Details
closure-compiler-stream through 0.1.15 allows execution of arbitrary commands. The argument `options` of the exports function in `index.js` can be controlled by users without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7603
- https://snyk.io/vuln/SNYK-JS-CLOSURECOMPILERSTREAM-560123
