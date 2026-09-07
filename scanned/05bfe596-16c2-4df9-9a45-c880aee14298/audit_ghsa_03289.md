# [C] Command injection in get-git-data

## Summary
Severity: Critical
Advisory: GHSA-wj6h-7chw-x4h2
CVE: CVE-2020-7619
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-wj6h-7chw-x4h2
Type: github-advisory

## Affected
- npm: `get-git-data` — affected >=0

## Details
get-git-data through 1.3.1 is vulnerable to Command Injection. It is possible to inject arbitrary commands as part of the arguments provided to get-git-data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7619
- https://github.com/chardos/get-git-data/blob/master/index.js#L7
- https://snyk.io/vuln/SNYK-JS-GETGITDATA-564222
