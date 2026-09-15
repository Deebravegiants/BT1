# [C] Command injection in fs-path

## Summary
Severity: Critical
Advisory: GHSA-8mrf-64fw-2x75
CVE: CVE-2020-8298
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-25
Source: https://github.com/advisories/GHSA-8mrf-64fw-2x75
Type: github-advisory

## Affected
- npm: `fs-path` — affected >=0 <0.0.25

## Details
fs-path node module before 0.0.25 is vulnerable to command injection by way of user-supplied inputs via the `copy`, `copySync`, `remove`, and `removeSync` methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8298
- https://github.com/pillys/fs-path/pull/6
- https://github.com/pillys/fs-path/commit/88ff5ee51046bb2c5d5e9c5afe6819b032092ce7
- https://hackerone.com/reports/324491
