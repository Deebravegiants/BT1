# [H] Combodo iTop: User enumeration via password reset

## Summary
Severity: High
Advisory: CVE-2026-27462
Aliases: GHSA-888g-gv33-xwwx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-27462
Type: osv

## Details
Combodo iTop is a web based IT service management tool. Prior to 3.2.3, iTop returns different responses for valid/invalid usernames depending on multiple factors in the reset password mechanism, leading to user enumeration. This issue has been fixed in version 3.2.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27462.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-888g-gv33-xwwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-27462
- https://github.com/Combodo/iTop/commit/9fd0ffd84ee62c1c6ede8d30db5fa0305f11fd01
