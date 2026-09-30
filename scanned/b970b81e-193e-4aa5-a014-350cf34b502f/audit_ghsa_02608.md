# [H] Code Injection in total.js

## Summary
Severity: High
Advisory: GHSA-vwhc-pww7-72x6
CVE: CVE-2021-32831
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-vwhc-pww7-72x6
Type: github-advisory

## Affected
- npm: `total.js` — affected >=0 <3.4.9

## Details
Total.js framework (npm package total.js) is a framework for Node.js platfrom written in pure JavaScript similar to PHP's Laravel or Python's Django or ASP.NET MVC. In total.js framework before version 3.4.9, calling the utils.set function with user-controlled values leads to code-injection. This can cause a variety of impacts that include arbitrary code execution. This is fixed in version 3.4.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32831
- https://github.com/totaljs/framework/commit/887b0fa9e162ef7a2dd9cec20a5ca122726373b3
- https://github.com/totaljs
- https://github.com/totaljs/framework/blob/e644167d5378afdc45cb0156190349b2c07ef235/changes.txt#L11
- https://securitylab.github.com/advisories/GHSL-2021-066-totaljs-totaljs
- https://www.npmjs.com/package/total.js
