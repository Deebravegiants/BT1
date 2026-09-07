# [M] Prototype Pollution in querymen

## Summary
Severity: Medium
Advisory: GHSA-p23c-p8w2-ww5v
CVE: CVE-2022-25871
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-18
Source: https://github.com/advisories/GHSA-p23c-p8w2-ww5v
Type: github-advisory

## Affected
- npm: `querymen` — affected >=0

## Details
All versions of package querymen are vulnerable to Prototype Pollution if the parameters of exported function handler(type, name, fn) can be controlled by users without any sanitization. Note: This vulnerability derives from an incomplete fix of [CVE-2020-7600](https://security.snyk.io/vuln/SNYK-JS-QUERYMEN-559867).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25871
- https://snyk.io/vuln/SNYK-JS-QUERYMEN-2391488
