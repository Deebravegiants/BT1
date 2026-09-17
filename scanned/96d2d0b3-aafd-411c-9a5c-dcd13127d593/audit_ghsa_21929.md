# [H] Command injection in git-parse

## Summary
Severity: High
Advisory: GHSA-m744-2jj8-vpfv
CVE: CVE-2021-26543
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-m744-2jj8-vpfv
Type: github-advisory

## Affected
- npm: `git-parse` — affected >=0 <1.0.5

## Details
The "gitDiff" function in Wayfair git-parse <=1.0.4 has a command injection vulnerability. Clients of the git-parse library are unlikely to be aware of this, so they might unwittingly write code that contains a vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26543
- https://advisory.checkmarx.net/advisory/CX-2020-4302
- https://github.com/wayfair/git-parse
- https://www.npmjs.com/package/git-parse
