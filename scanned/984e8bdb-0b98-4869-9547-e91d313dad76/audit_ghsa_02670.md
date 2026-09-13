# [C] Incorrect Authorization in serverless-offline

## Summary
Severity: Critical
Advisory: GHSA-h97f-5258-5593
CVE: CVE-2021-38384
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-h97f-5258-5593
Type: github-advisory

## Affected
- npm: `serverless-offline` — affected >=0

## Details
Serverless Offline 8.0.0 returns a 403 HTTP status code for a route that has a trailing `/` character, which might cause a developer to implement incorrect access control, because the actual behavior within the Amazon AWS environment is a 200 HTTP status code (i.e., possibly greater than expected permissions).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38384
- https://github.com/dherault/serverless-offline/issues/1259
- https://github.com/dherault/serverless-offline
