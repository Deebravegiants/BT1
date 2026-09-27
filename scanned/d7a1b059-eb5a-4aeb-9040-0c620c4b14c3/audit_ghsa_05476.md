# [M] askbot inexhaustive permissions check allows any user to modify a different user's profile picture

## Summary
Severity: Medium
Advisory: GHSA-r2jv-fwfr-4j8c
CVE: CVE-2026-1213
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-r2jv-fwfr-4j8c
Type: github-advisory

## Affected
- PyPI: `askbot` — affected >=0 <0.12.3

## Details
All versions of askbot before and including 0.12.2 allow an attacker authenticated with normal user permissions to modify the profile picture of other application users. This issue affects askbot: 0.12.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1213
- https://github.com/ASKBOT/askbot-devel/commit/3da3d75f35204aa71633c7a315327ba39cb6295d
- https://askbot.com
- https://fluidattacks.com/advisories/ghost
- https://github.com/askbot/askbot-devel
