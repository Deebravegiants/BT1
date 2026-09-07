# [C] Command injection in github-todos

## Summary
Severity: Critical
Advisory: GHSA-792j-9wj3-j634
CVE: CVE-2021-44684
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-792j-9wj3-j634
Type: github-advisory

## Affected
- npm: `github-todos` — affected >=0

## Details
naholyr github-todos 3.1.0 is vulnerable to command injection. The range argument for the _hook subcommand is concatenated without any validation, and is directly used by the exec function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44684
- https://github.com/dwisiswant0/advisory/issues/5
- https://advisory.dw1.io/5
