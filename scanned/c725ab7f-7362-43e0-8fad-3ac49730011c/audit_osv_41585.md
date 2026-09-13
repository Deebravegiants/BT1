# [C] grav-plugin-api < 1.0.6 Privilege Escalation via createApiKey

## Summary
Severity: Critical
Advisory: CVE-2026-62233
Aliases: CVE-2026-62666, GHSA-8gg4-rvvv-cq96
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62233
Type: osv

## Details
grav-plugin-api before 1.0.6 fails to validate super-admin status in createApiKey, generate2fa, and disable2fa endpoints, allowing non-super api.users.write managers to escalate to super-admin. Attackers can mint API keys bound to super-admin accounts or strip 2FA from super-admin users to achieve full instance takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62233.json
- https://github.com/getgrav/grav/security/advisories/GHSA-8gg4-rvvv-cq96
- https://nvd.nist.gov/vuln/detail/CVE-2026-62233
- https://www.vulncheck.com/advisories/grav-plugin-api-privilege-escalation-via-createapikey
- https://github.com/getgrav/grav
