# [M] Capgo - Unauthenticated RBAC Bindings and Email Disclosure via get_org_user_access_rbac NULL-auth Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-56219
Aliases: GHSA-vvm7-xhcj-m94h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-56219
Type: osv

## Details
Capgo before 12.128.2 contains a NULL-auth bypass vulnerability in the public.get_org_user_access_rbac function that allows unauthenticated attackers to retrieve RBAC role bindings and member email addresses. Attackers can exploit improper NULL comparison in the authorization gate to disclose organization membership, roles, and email addresses via the PostgREST RPC endpoint using only a public API key.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56219.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-vvm7-xhcj-m94h
- https://nvd.nist.gov/vuln/detail/CVE-2026-56219
- https://www.vulncheck.com/advisories/capgo-unauthenticated-rbac-bindings-and-email-disclosure-via-get-org-user-access-rbac-null-auth-bypass
