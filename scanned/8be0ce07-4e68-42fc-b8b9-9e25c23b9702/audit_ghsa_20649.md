# [C] @pendo324/get-process-by-name are vulnerable to Arbitrary Code Execution

## Summary
Severity: Critical
Advisory: GHSA-qhxv-296x-hjv7
CVE: CVE-2022-25644
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-29
Source: https://github.com/advisories/GHSA-qhxv-296x-hjv7
Type: github-advisory

## Affected
- npm: `@pendo324/get-process-by-name` — affected >=0

## Details
All versions of package @pendo324/get-process-by-name are vulnerable to Arbitrary Code Execution due to improper sanitization of getProcessByName function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25644
- https://github.com/pendo324/get-process-by-name-js
- https://github.com/pendo324/get-process-by-name-js/blob/34e8a279a94fa23acb13e302e9516ab1ea8d8731/index.js%23L27-L28
- https://security.snyk.io/vuln/SNYK-JS-PENDO324GETPROCESSBYNAME-2419094
