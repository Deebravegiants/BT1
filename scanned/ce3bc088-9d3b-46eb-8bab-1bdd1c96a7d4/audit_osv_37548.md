# [H] Runtipi unauthenticated /api/auth/reset-password allows operator account takeover during active reset window

## Summary
Severity: High
Advisory: CVE-2026-31881
Aliases: GHSA-96fm-whrc-cwg3
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31881
Type: osv

## Details
Runtipi is a personal homeserver orchestrator. Prior to 4.8.0, an unauthenticated attacker can reset the operator (admin) password when a password-reset request is active, resulting in full account takeover. The endpoint POST /api/auth/reset-password is exposed without authentication/authorization checks. During the 15-minute reset window, any remote user can set a new operator password and log in as admin. This vulnerability is fixed in 4.8.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31881.json
- https://github.com/runtipi/runtipi/security/advisories/GHSA-96fm-whrc-cwg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-31881
