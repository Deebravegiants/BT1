# [H] Improper rate limiting in Koel

## Summary
Severity: High
Advisory: GHSA-r37h-j483-cjjm
CVE: CVE-2021-33563
CWE: CWE-799, CWE-916
Ecosystem: Packagist
Published: 2021-06-01
Source: https://github.com/advisories/GHSA-r37h-j483-cjjm
Type: github-advisory

## Affected
- Packagist: `phanan/koel` — affected >=0 <5.1.4

## Details
Koel before 5.1.4 lacks login throttling, lacks a password strength policy, and shows whether a failed login attempt had a valid username. This might make brute-force attacks easier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33563
- https://github.com/koel/koel/releases/tag/v5.1.4
- https://huntr.dev/bounties/1-other-koel/koel
