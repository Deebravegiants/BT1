# [C] gitblame susceptible to command injection

## Summary
Severity: Critical
Advisory: GHSA-3486-rvxc-hrrj
CVE: CVE-2020-28434
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-03
Source: https://github.com/advisories/GHSA-3486-rvxc-hrrj
Type: github-advisory

## Affected
- npm: `gitblame` — affected >=0

## Details
A command injection vulnerability affects all versions of package gitblame. The injection point is located in line 15 in lib/gitblame.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28434
- https://github.com/xjamundx/gitblame
- https://github.com/xjamundx/gitblame/blob/master/lib/gitblame.js#L15
- https://security.snyk.io/vuln/SNYK-JS-GITBLAME-1050430
