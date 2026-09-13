# [H] file-type vulnerable to Infinite Loop via malformed MKV file

## Summary
Severity: High
Advisory: GHSA-mhxj-85r3-2x55
CVE: CVE-2022-36313
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-22
Source: https://github.com/advisories/GHSA-mhxj-85r3-2x55
Type: github-advisory

## Affected
- npm: `file-type` — affected >=13.0.0 <16.5.4
- npm: `file-type` — affected >=17.0.0 <17.1.3

## Details
An issue was discovered in the file-type package from 13.0.0 until 16.5.4 and 17.x before 17.1.3 for Node.js. A malformed MKV file could cause the file type detector to get caught in an infinite loop. This would make the application become unresponsive and could be used to cause a DoS attack when used on a web server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36313
- https://github.com/sindresorhus/file-type/commit/2c4d1200c99dffb7d515b9b9951ef43c22bf7e47
- https://github.com/sindresorhus/file-type/commit/8f981c32e2750d2516457e305e502ee2ad715759#diff-c853b2249e99790d8725774cf63c90c5ab17112067df6e267f3701d7bf591d12
- https://github.com/sindresorhus/file-type/commit/d86835680f4cccbee1a60628783c36700ec9e254
- https://github.com/sindresorhus/file-type
- https://github.com/sindresorhus/file-type/compare/v12.4.2...v13.0.0#diff-c853b2249e99790d8725774cf63c90c5ab17112067df6e267f3701d7bf591d12R611-R613
- https://github.com/sindresorhus/file-type/releases/tag/v16.5.4
- https://github.com/sindresorhus/file-type/releases/tag/v17.1.3
- https://security.netapp.com/advisory/ntap-20220909-0005
- https://security.snyk.io/vuln/SNYK-JS-FILETYPE-2958042
- https://www.npmjs.com/package/file-type
