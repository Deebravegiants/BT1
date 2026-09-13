# [C] Code Injection in node-extend

## Summary
Severity: Critical
Advisory: GHSA-cg42-4wrc-gp47
CVE: CVE-2020-7673
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-cg42-4wrc-gp47
Type: github-advisory

## Affected
- npm: `node-extend` — affected >=0

## Details
node-extend through 0.2.0 is vulnerable to Arbitrary Code Execution. User input provided to the argument `A` of `extend` function`(A,B,as,isAargs)` located within `lib/extend.js` is executed by the `eval` function, resulting in code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7673
- https://snyk.io/vuln/SNYK-JS-NODEEXTEND-571491
