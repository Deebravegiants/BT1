# [C] check-branches is vulnerable to command Injection

## Summary
Severity: Critical
Advisory: GHSA-9c4g-fp4r-prrv
CVE: CVE-2025-11148
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-9c4g-fp4r-prrv
Type: github-advisory

## Affected
- npm: `check-branches` — affected >=0

## Details
All versions of the package check-branches are vulnerable to Command Injection.

check-branches is a command-line tool that is interacted with locally, or via CI, to confirm no conflicts exist in git branches.

However, the library follows these conventions which can be abused:
1. It trusts branch names as they are (plain text)
2. It spawns git commands by concatenating user input

Since a branch name is potentially a user input - as users can create branches remotely via pull requests, or simply due to privileged access to a repository - it can effectively be abused to run any command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11148
- https://gist.github.com/lirantal/054b4ad039a86c418f2c84e3e884d6ec
- https://github.com/puntorigen/check-branches
- https://security.snyk.io/vuln/SNYK-JS-CHECKBRANCHES-2766494
