# [M] Reverse Tabnapping in swagger-ui

## Summary
Severity: Medium
Advisory: GHSA-x9p2-fxq6-2m5f
CWE: CWE-1022
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-06-20
Source: https://github.com/advisories/GHSA-x9p2-fxq6-2m5f
Type: github-advisory

## Affected
- npm: `swagger-ui` — affected >=0 <3.18.0

## Details
Versions of `swagger-ui` prior to 3.18.0 are vulnerable to [Reverse Tabnapping](https://www.owasp.org/index.php/Reverse_Tabnabbing). The package uses `target='_blank'` in anchor tags, allowing attackers to access `window.opener` for the original page. This is commonly used for phishing attacks.


## Recommendation

Upgrade to version 3.18.0 or later.

## References
- https://github.com/swagger-api/swagger-ui/pull/4789
- https://github.com/swagger-api/swagger-ui/commit/3f4cae3334fdd492a373f4453bd03a9ebd87becf
- https://github.com/swagger-api/swagger-ui/releases/tag/v3.18.0
- https://snyk.io/vuln/SNYK-JS-SWAGGERUI-449808
- https://www.npmjs.com/advisories/975
