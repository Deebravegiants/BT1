# [C] Shiori Authenticated Privilege Escalation via PATCH /api/v1/auth/account

## Summary
Severity: Critical
Advisory: CVE-2026-61463
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-61463
Type: osv

## Details
Shiori contains a privilege escalation vulnerability in the account update endpoint that allows authenticated users to modify the owner field without authorization checks. Attackers can escalate to administrator by submitting a crafted PATCH request with owner: true, then re-authenticate to obtain an admin JWT token granting full system access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61463.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-61463
- https://www.vulncheck.com/advisories/shiori-authenticated-privilege-escalation-via-patch-api-v1-auth-account
- https://github.com/go-shiori/shiori/issues/1196
- https://github.com/go-shiori/shiori/commit/6c8a7dbc11b131609bfda736b14d61c51f9027b2
- https://github.com/go-shiori/shiori
