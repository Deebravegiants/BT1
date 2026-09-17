# [H] mc-kill-port vulnerable to Arbitrary Command Execution via kill function

## Summary
Severity: High
Advisory: GHSA-2cg4-7q4x-7rr2
CVE: CVE-2022-25973
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-11
Source: https://github.com/advisories/GHSA-2cg4-7q4x-7rr2
Type: github-advisory

## Affected
- npm: `mc-kill-port` — affected >=0

## Details
All versions of package mc-kill-port are vulnerable to Arbitrary Command Execution via the `kill` function, due to missing sanitization of the `port` argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25973
- https://security.snyk.io/vuln/SNYK-JS-MCKILLPORT-2419070
- https://www.npmjs.com/package/mc-kill-port
