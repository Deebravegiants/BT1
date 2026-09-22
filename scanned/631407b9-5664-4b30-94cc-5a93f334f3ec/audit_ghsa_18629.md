# [M] BBOT's git_clone.py can expose users' GitHub API keys to an attacker-controlled webserver

## Summary
Severity: Medium
Advisory: GHSA-63wh-p5fx-h4vc
CVE: CVE-2025-10281
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-63wh-p5fx-h4vc
Type: github-advisory

## Affected
- PyPI: `bbot` — affected >=0 <2.7.0

## Details
### Summary

Due to unsafe URL handling, bbot's `git_clone.py` can be made to leak a user's github.com API key to an attacker-controlled webserver.

### Impact

A user who has placed their github.com API key in the configuration for any of the following modules:

* `github_codesearch`
* `github_workflows`
* `gitlab`
* `git_clone`
* `github_usersearch`
* `github_org`

may leak it to an untrustworthy server.

## References
- https://github.com/blacklanternsecurity/bbot/security/advisories/GHSA-63wh-p5fx-h4vc
- https://nvd.nist.gov/vuln/detail/CVE-2025-10281
- https://github.com/blacklanternsecurity/bbot/commit/0ede97fa887de33fcfd1378b4213a09c21dc6140
- https://blog.blacklanternsecurity.com/p/bbot-security-advisory-gitdumper
- https://github.com/blacklanternsecurity/bbot
