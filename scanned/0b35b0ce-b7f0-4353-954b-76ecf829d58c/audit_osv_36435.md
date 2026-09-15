# [M] Blinko: IDOR - user.detail Endpoint Leaks Superadmin Token

## Summary
Severity: Medium
Advisory: CVE-2026-23487
Aliases: GHSA-4ffv-78qx-9p66
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-23487
Type: osv

## Details
Blinko is an AI-powered card note-taking project. Prior to version 1.8.4, there is an IDOR vulnerability where user.detail Endpoint Leaks the Superadmin Token. This issue has been patched in version 1.8.4.

## References
- https://github.com/blinkospace/blinko/releases/tag/1.8.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23487.json
- https://github.com/blinkospace/blinko/security/advisories/GHSA-4ffv-78qx-9p66
- https://nvd.nist.gov/vuln/detail/CVE-2026-23487
- https://github.com/blinkospace/blinko/commit/bef6b770743e87c630db2d00d7049dabd96bfe85
