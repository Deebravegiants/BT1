# [H] Command injection in total.js

## Summary
Severity: High
Advisory: GHSA-4449-hg37-77v8
CVE: CVE-2020-28494
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-02-05
Source: https://github.com/advisories/GHSA-4449-hg37-77v8
Type: github-advisory

## Affected
- npm: `total.js` — affected >=0 <3.4.7

## Details
There is a command injection vulnerability that affects the package total.js before version 3.4.7. The issue occurs in the image.pipe and image.stream functions. The type parameter is used to build the command that is then executed using child_process.spawn. The issue occurs because child_process.spawn is called with the option shell set to true and because the type parameter is not properly sanitized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28494
- https://github.com/totaljs/framework/commit/6192491ab2631e7c1d317c221f18ea613e2c18a5
- https://snyk.io/vuln/SNYK-JS-TOTALJS-1046672
- https://www.npmjs.com/package/total.js
