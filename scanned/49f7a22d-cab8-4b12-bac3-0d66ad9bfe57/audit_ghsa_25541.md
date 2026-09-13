# [C] Command injection in git-interface

## Summary
Severity: Critical
Advisory: GHSA-qffw-8wg7-h665
CVE: CVE-2022-1440
CWE: CWE-78, CWE-88
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-qffw-8wg7-h665
Type: github-advisory

## Affected
- npm: `git-interface` — affected >=0 <2.1.2

## Details
A command injection vulnerability exists in git-interface in the GitHub repository yarkeev/git-interface prior to 2.1.2. If both the git remote and destination directory are provided by user input, then the use of an `--upload-pack` command-line argument feature of git is also supported for `git clone`, which would then allow for any operating system command to be spawned by the attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1440
- https://github.com/yarkeev/git-interface/commit/f828aa790016fee3aa667f7b44cf94bf0aa8c60d
- https://github.com/yarkeev/git-interface
- https://huntr.dev/bounties/cdc25408-d3c1-4a9d-bb45-33b12a715ca1
