# [H] Denial of Service in axios

## Summary
Severity: High
Advisory: GHSA-42xw-2xvc-qx8m
CVE: CVE-2019-10742
CWE: CWE-20, CWE-755
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-05-29
Source: https://github.com/advisories/GHSA-42xw-2xvc-qx8m
Type: github-advisory

## Affected
- npm: `axios` — affected >=0 <0.18.1

## Details
Versions of `axios` prior to 0.18.1 are vulnerable to Denial of Service. If a request exceeds the `maxContentLength` property, the package prints an error but does not stop the request. This may cause high CPU usage and lead to Denial of Service.


## Recommendation

Upgrade to 0.18.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10742
- https://github.com/axios/axios/issues/1098
- https://github.com/axios/axios/pull/1485
- https://github.com/axios/axios/commit/acabfbdf00a58bb866c9d070e8a10d1d0dbeb572
- https://app.snyk.io/vuln/SNYK-JS-AXIOS-174505
- https://snyk.io/vuln/SNYK-JS-AXIOS-174505
- https://www.npmjs.com/advisories/880
