# [H] Command injection in simple-git

## Summary
Severity: High
Advisory: GHSA-28xr-mwxg-3qc8
CVE: CVE-2022-24066
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-02
Source: https://github.com/advisories/GHSA-28xr-mwxg-3qc8
Type: github-advisory

## Affected
- npm: `simple-git` — affected >=0 <3.5.0

## Details
`simple-git` (maintained as [git-js](https://github.com/steveukx/git-js) named repository on GitHub) is a light weight interface for running git commands in any node.js application.The package simple-git before 3.5.0 are vulnerable to Command Injection due to an incomplete fix of [CVE-2022-24433](https://security.snyk.io/vuln/SNYK-JS-SIMPLEGIT-2421199) which only patches against the git fetch attack vector. A similar use of the --upload-pack feature of git is also supported for git clone, which the prior fix didn't cover. A fix was released in simple-git@3.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24066
- https://github.com/steveukx/git-js/commit/2040de601c894363050fef9f28af367b169a56c5
- https://gist.github.com/lirantal/a930d902294b833514e821102316426b
- https://github.com/steveukx/git-js
- https://github.com/steveukx/git-js/releases/tag/simple-git%403.5.0
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2434820
- https://snyk.io/vuln/SNYK-JS-SIMPLEGIT-2434306
