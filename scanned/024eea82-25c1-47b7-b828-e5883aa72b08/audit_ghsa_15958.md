# [M] git-shallow-clone Argument Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qwrq-vxvw-537r
CVE: CVE-2024-21531
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-10-01
Source: https://github.com/advisories/GHSA-qwrq-vxvw-537r
Type: github-advisory

## Affected
- npm: `git-shallow-clone` — affected >=0

## Details
All versions of the package git-shallow-clone are vulnerable to Argument injection due to missing sanitization or mitigation flags in the process variable of the gitShallowClone function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21531
- https://github.com/10uei011/git-shallow-clone
- https://github.com/10uei011/git-shallow-clone/blob/master/index.js#L27
- https://security.snyk.io/vuln/SNYK-JS-GITSHALLOWCLONE-3253853
