# [M] Cross-site Scripting in file-upload-with-preview

## Summary
Severity: Medium
Advisory: GHSA-97pv-4338-r5vp
CVE: CVE-2021-23439
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-97pv-4338-r5vp
Type: github-advisory

## Affected
- npm: `file-upload-with-preview` — affected >=0 <4.2.0

## Details
This affects the package file-upload-with-preview before 4.2.0. A file containing malicious JavaScript code in the name can be uploaded (a user needs to be tricked into uploading such a file).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23439
- https://github.com/johndatserakis/file-upload-with-preview/pull/40/files?file-filters%5B%5D=.js&hide-deleted-files=true%23diff-fe47b243de17419c0daa22cd785cd754baed60cf3679d3da1d6fe006f9f4a7f0R174
- https://github.com/johndatserakis/file-upload-with-preview
- https://github.com/johndatserakis/file-upload-with-preview/blob/develop/src/file-upload-with-preview.js%23L168
- https://snyk.io/vuln/SNYK-JS-FILEUPLOADWITHPREVIEW-1579492
