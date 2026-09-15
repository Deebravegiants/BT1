# [M] Code injection in npm git

## Summary
Severity: Medium
Advisory: GHSA-9gqr-xp86-f87h
CVE: CVE-2021-23632
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-9gqr-xp86-f87h
Type: github-advisory

## Affected
- npm: `git` — affected >=0

## Details
All versions of package git are vulnerable to Remote Code Execution (RCE) due to missing sanitization in the Git.git method, which allows execution of OS commands rather than just git commands. At this time, there is no known workaround. There has been no patch released.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23632
- https://snyk.io/vuln/SNYK-JS-GIT-1568518
