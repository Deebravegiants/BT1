# [H] Capgo - Privilege Escalation via Broken Row Level Security in org_users

## Summary
Severity: High
Advisory: CVE-2026-56251
Aliases: GHSA-9xqh-f26v-9c9h
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2026-56251
Type: osv

## Details
Capgo before 12.128.2 contains a broken row level security policy in the org_users table that allows authenticated users to elevate privileges from admin to super_admin. Attackers can exploit the insufficient RLS enforcement to gain unauthorized super_admin access and compromise system security.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56251.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-9xqh-f26v-9c9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-56251
- https://www.vulncheck.com/advisories/capgo-privilege-escalation-via-broken-row-level-security-in-org-users
