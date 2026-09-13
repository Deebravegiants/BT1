# [C] Command injection in eslint-fixer

## Summary
Severity: Critical
Advisory: GHSA-45w5-pvr8-4rh5
CVE: CVE-2021-26275
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-45w5-pvr8-4rh5
Type: github-advisory

## Affected
- npm: `eslint-fixer` — affected >=0

## Details
The eslint-fixer package through 0.1.5 for Node.js allows command injection via shell metacharacters to the fix function. NOTE: This vulnerability only affects products that are no longer supported by the maintainer. The ozum/eslint-fixer GitHub repository has been intentionally deleted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26275
- https://advisory.checkmarx.net/advisory/CX-2021-4774
- https://www.npmjs.com/package/eslint-fixer
