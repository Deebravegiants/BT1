# [H] Express-FileUpload Arbitrary File Overwrite

## Summary
Severity: High
Advisory: GHSA-w4m6-x6c2-j5c9
CVE: CVE-2022-27261
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-w4m6-x6c2-j5c9
Type: github-advisory

## Affected
- npm: `express-fileupload` — affected >=0

## Details
An arbitrary file write vulnerability in Express-FileUpload v1.3.1 allows attackers to upload multiple files with the same name, causing an overwrite of files in the web application server. This vulnerability is [debated by the package author](https://github.com/richardgirges/express-fileupload/issues/316).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27261
- https://github.com/richardgirges/express-fileupload/issues/312
- https://github.com/richardgirges/express-fileupload/issues/316
- https://github.com/richardgirges/express-fileupload
- https://www.npmjs.com/package/express-fileupload
- https://www.youtube.com/watch?v=3ROHB3ck4tA
