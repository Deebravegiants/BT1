# [M] Capgo - Unauthenticated Organization Member Email Disclosure via get_org_members RPC

## Summary
Severity: Medium
Advisory: CVE-2026-56253
Aliases: GHSA-x34h-gc65-f6g4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2026-56253
Type: osv

## Details
Capgo before 12.128.2 contains an improper access control vulnerability in the public.get_org_members RPC function that allows unauthenticated attackers to enumerate organization members. Attackers can invoke the endpoint using only the public sb_publishable_* key and an organization UUID to retrieve sensitive member information including email addresses, user IDs, roles, and pending invitations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56253.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-x34h-gc65-f6g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-56253
- https://www.vulncheck.com/advisories/capgo-unauthenticated-organization-member-email-disclosure-via-get-org-members-rpc
