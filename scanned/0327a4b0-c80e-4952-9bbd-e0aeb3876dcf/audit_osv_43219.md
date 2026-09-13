# [H] Budibase before 3.40.0 Authentication Bypass via Tenant Owner Email

## Summary
Severity: High
Advisory: CVE-2026-72856
Aliases: GHSA-j82g-67x3-xcwh
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-72856
Type: osv

## Details
Budibase versions before 3.40.0 contain an authorization/authentication bypass in the PUT /api/global/users/tenant/owner (changeTenantOwnerEmail) endpoint. On self-hosted instances (SELF_HOSTED or DISABLE_ACCOUNT_PORTAL set), the cloudRestricted middleware is a no-op and the route is protected only by a general authentication check, so any authenticated user — including a lowest-privilege BASIC app user — can reassign the tenant account-holder (top-privilege admin) email to an attacker-controlled address. The attacker can then use the public password-reset flow to take over the admin account, leading to full administrative access.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-j82g-67x3-xcwh
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72856.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72856
- https://www.vulncheck.com/advisories/budibase-before-authentication-bypass-via-tenant-owner-email
