# [C] Crabbox < 0.9.0 Authentication Bypass via Admin Claim Injection

## Summary
Severity: Critical
Advisory: CVE-2026-45223
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-45223
Type: osv

## Details
Crabbox before 0.9.0 contains an authentication bypass vulnerability in the coordinator user-token verification path where the verifyUserToken() function fails to reject payloads containing an admin claim, allowing attackers to escalate privileges. An attacker with access to the shared non-admin token can craft a user-token payload with admin: true, sign it using HMAC-SHA256, and present it to admin-only coordinator routes to gain full coordinator admin access including lease visibility, pool state management, and forced release operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45223.json
- https://github.com/openclaw/crabbox/releases/tag/v0.9.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-45223
- https://www.vulncheck.com/advisories/crabbox-authentication-bypass-via-admin-claim-injection
- https://github.com/openclaw/crabbox/pull/64
- https://github.com/openclaw/crabbox/commit/46079f6de7f10cf61bc47efebd0c143a41664898
- https://github.com/openclaw/crabbox
