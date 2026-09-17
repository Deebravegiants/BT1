# [M] Axios Cross-Site Request Forgery Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wf5p-g6vw-rhxx
CVE: CVE-2023-45857
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-08
Source: https://github.com/advisories/GHSA-wf5p-g6vw-rhxx
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.6.0
- npm: `axios` — affected >=0.8.1 <0.28.0

## Details
An issue discovered in Axios 0.8.1 through 1.5.1 inadvertently reveals the confidential XSRF-TOKEN stored in cookies by including it in the HTTP header X-XSRF-TOKEN for every request made to any host allowing attackers to view sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45857
- https://github.com/axios/axios/issues/6006
- https://github.com/axios/axios/issues/6022
- https://github.com/axios/axios/pull/6028
- https://github.com/axios/axios/pull/6091
- https://github.com/axios/axios/commit/2755df562b9c194fba6d8b609a383443f6a6e967
- https://github.com/axios/axios/commit/96ee232bd3ee4de2e657333d4d2191cd389e14d0
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v0.28.0
- https://github.com/axios/axios/releases/tag/v1.6.0
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://security.snyk.io/vuln/SNYK-JS-AXIOS-6032459
