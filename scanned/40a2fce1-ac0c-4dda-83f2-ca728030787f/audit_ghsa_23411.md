# [C] Gitea Allows 1FA Even for 2FA-Enrolled Accounts

## Summary
Severity: Critical
Advisory: GHSA-3393-r4p5-vhqh
CVE: CVE-2019-11576
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3393-r4p5-vhqh
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.8.0

## Details
Gitea before 1.8.0 allows 1FA for user accounts that have completed 2FA enrollment. If a user's credentials are known, then an attacker could send them to the API without requiring the 2FA one-time password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11576
- https://github.com/go-gitea/gitea/pull/6674
- https://github.com/go-gitea/gitea/pull/6676
- https://blog.gitea.io/2019/04/gitea-1.8.0-is-released
- https://github.com/go-gitea/gitea
