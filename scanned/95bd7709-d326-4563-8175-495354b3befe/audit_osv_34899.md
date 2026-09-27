# [C] OrangeHRM is Vulnerable to Persistent Session Access Due to Missing Invalidation After User Disable and Password Change

## Summary
Severity: Critical
Advisory: CVE-2025-66289
Aliases: GHSA-99qp-xh4q-pr9x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-66289
Type: osv

## Details
OrangeHRM is a comprehensive human resource management (HRM) system. From version 5.0 to 5.7, the application does not invalidate existing sessions when a user is disabled or when a password change occurs, allowing active session cookies to remain valid indefinitely. As a result, a disabled user, or an attacker using a compromised account, can continue to access protected pages and perform operations as long as a prior session remains active. Because the server performs no session revocation or session-store cleanup during these critical state changes, disabling an account or updating credentials has no effect on already-established sessions. This makes administrative disable actions ineffective and allows unauthorized users to retain full access even after an account is closed or a password is reset, exposing the system to prolonged unauthorized use and significantly increasing the impact of account takeover scenarios. This issue has been patched in version 5.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66289.json
- https://github.com/orangehrm/orangehrm/security/advisories/GHSA-99qp-xh4q-pr9x
- https://nvd.nist.gov/vuln/detail/CVE-2025-66289
