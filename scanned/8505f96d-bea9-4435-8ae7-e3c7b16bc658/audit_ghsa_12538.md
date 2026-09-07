# [H] git-commit-info vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-h42j-mrmp-9369
CVE: CVE-2023-26134
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-28
Source: https://github.com/advisories/GHSA-h42j-mrmp-9369
Type: github-advisory

## Affected
- npm: `git-commit-info` — affected >=0 <2.0.2

## Details
Versions of the package git-commit-info before 2.0.2 are vulnerable to Command Injection such that the package-exported method gitCommitInfo() fails to sanitize its parameter commit, which later flows into a sensitive command execution API. As a result, attackers may inject arguments to the git binary.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26134
- https://github.com/JPeer264/node-git-commit-info/issues/24
- https://github.com/JPeer264/node-git-commit-info/commit/f7c491ede51f886a988af9b266797cb24591d18c
- https://github.com/JPeer264/node-git-commit-info
- https://security.snyk.io/vuln/SNYK-JS-GITCOMMITINFO-5740174
- https://www.npmjs.com/package/execa/v/5.1.0#execacommandcommand-options
