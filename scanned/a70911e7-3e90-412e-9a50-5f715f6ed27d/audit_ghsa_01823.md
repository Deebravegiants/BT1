# [C] Command injection in git-it-electron

## Summary
Severity: Critical
Advisory: GHSA-wjqc-j537-j9gj
CVE: CVE-2021-44685
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-08
Source: https://github.com/advisories/GHSA-wjqc-j537-j9gj
Type: github-advisory

## Affected
- npm: `git-it-electron` — affected >=0

## Details
Git-it through 4.4.0 allows OS command injection at the Branches Aren't Just For Birds challenge step. During the verification process, it attempts to run the reflog command followed by the current branch name (which is not sanitized for execution).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44685
- https://github.com/dwisiswant0/advisory/issues/3
- https://advisory.dw1.io/3
- https://github.com/jlord/git-it-electron
- https://github.com/jlord/git-it-electron/releases
