# [C] OS Command Injection in git-pull-or-clone

## Summary
Severity: Critical
Advisory: GHSA-3x62-x456-q2vm
CVE: CVE-2022-24437
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-3x62-x456-q2vm
Type: github-advisory

## Affected
- npm: `git-pull-or-clone` — affected >=0 <2.0.2

## Details
The package git-pull-or-clone before 2.0.2 is vulnerable to Command Injection due to the use of the --upload-pack feature of git which is also supported for git clone. The source includes the use of the secure child process API spawn(). However, the outpath parameter passed to it may be a command-line argument to the git clone command and result in arbitrary command injection.
## Credits

Credit @lirantal for discovering this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24437
- https://github.com/feross/git-pull-or-clone/commit/f9ce092be13cc32e685dfa26e7705e9c6e3108a3
- https://gist.github.com/lirantal/327e9dd32686991b5a1fa6341aac2e7b
- https://github.com/feross/git-pull-or-clone
- https://snyk.io/vuln/SNYK-JS-GITPULLORCLONE-2434307
