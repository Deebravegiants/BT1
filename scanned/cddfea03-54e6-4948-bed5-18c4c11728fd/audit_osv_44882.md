# [M] PasswordPusher before 2.11.1 Race Condition View Limit Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-87816
Aliases: GHSA-6q3c-57pp-wvpp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87816
Type: osv

## Details
PasswordPusher before 2.11.1 contains a time-of-check-to-time-of-use race condition in view limit enforcement that allows unauthenticated attackers to bypass expire_after_views limits. Attackers can send concurrent requests to the show endpoint to access one-time secrets multiple times before the view count is incremented and the push expires.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87816.json
- https://github.com/pglombardo/PasswordPusher/security/advisories/GHSA-6q3c-57pp-wvpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-87816
- https://www.vulncheck.com/advisories/passwordpusher-before-2.11.1-race-condition-view-limit-bypass
