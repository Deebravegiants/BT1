# [H] codecov NPM module allows remote attackers to execute arbitrary commands

## Summary
Severity: High
Advisory: GHSA-5q88-cjfq-g2mh
CVE: CVE-2020-7597
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-19
Source: https://github.com/advisories/GHSA-5q88-cjfq-g2mh
Type: github-advisory

## Affected
- npm: `codecov` — affected >=0 <3.6.5

## Details
codecov-node npm module before 3.6.5 allows remote attackers to execute arbitrary commands.The value provided as part of the gcov-root argument is executed by the exec function within lib/codecov.js. This vulnerability exists due to an incomplete fix of CVE-2020-7596.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7597
- https://github.com/codecov/codecov-node/commit/02cf13d8b93ac547b5b4c2cfe186b7d874fd234f
- https://snyk.io/vuln/SNYK-JS-CODECOV-548879
