# [H] simple-git is vulnerable to Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-hffm-xvc3-vprc
CVE: CVE-2026-6951
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-hffm-xvc3-vprc
Type: github-advisory

## Affected
- npm: `simple-git` — affected >=0 <3.36.0

## Details
Versions of the package simple-git before 3.36.0 are vulnerable to Remote Code Execution (RCE) due to an incomplete fix for [CVE-2022-25912](https://security.snyk.io/vuln/SNYK-JS-SIMPLEGIT-3112221) that blocks the -c option but not the equivalent --config form. If untrusted input can reach the options argument passed to simple-git, an attacker may still achieve remote code execution by enabling protocol.ext.allow=always and using an ext:: clone source.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6951
- https://github.com/steveukx/git-js/commit/89a2294febed5dfe737c4c735d936bb6018746a8
- https://gist.github.com/KKC73/02d1d97f3410756095b501fda0ac8ca6
- https://github.com/steveukx/git-js
- https://security.snyk.io/vuln/SNYK-JS-SIMPLEGIT-15456078
