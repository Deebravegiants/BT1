# [H] Prototype pollution in total.js

## Summary
Severity: High
Advisory: GHSA-6cf8-qhqj-vjqm
CVE: CVE-2020-28495
CWE: CWE-1321, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-02-05
Source: https://github.com/advisories/GHSA-6cf8-qhqj-vjqm
Type: github-advisory

## Affected
- npm: `total.js` — affected >=0 <3.4.7

## Details
There is a prototype pollution vulnerability in the package total.js before version 3.4.7. The set function can be used to set a value into the object according to the path. However the keys of the path being set are not properly sanitized, leading to a prototype pollution vulnerability. The impact depends on the application. In some cases it is possible to achieve Denial of service (DoS), Remote Code Execution or Property Injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28495
- https://github.com/totaljs/framework/commit/b3f901561d66ab799a4a99279893b94cad7ae4ff
- https://docs.totaljs.com/latest/en.html%23api~FrameworkUtils~U.set
- https://github.com/totaljs/framework/blob/master/utils.js%23L6606
- https://github.com/totaljs/framework/blob/master/utils.js%23L6617
- https://snyk.io/vuln/SNYK-JS-TOTALJS-1046671
- https://www.npmjs.com/package/total.js
