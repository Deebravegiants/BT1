# [M] Capgo - Unauthenticated Organization Enumeration and Billing Status Disclosure via Supabase RPC

## Summary
Severity: Medium
Advisory: CVE-2026-56214
Aliases: GHSA-mh5p-rrhp-442q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-20
Source: https://osv.dev/vulnerability/CVE-2026-56214
Type: osv

## Details
Capgo before 12.128.2 contains an information disclosure vulnerability in Supabase PostgREST RPC endpoints is_trial_org and is_paying_org that allows unauthenticated attackers to enumerate organizations and disclose billing status using the public sb_publishable key. Attackers can invoke these endpoints to determine organization existence via distinguishable return values and identify paying customers for targeted profiling.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56214.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-mh5p-rrhp-442q
- https://nvd.nist.gov/vuln/detail/CVE-2026-56214
- https://www.vulncheck.com/advisories/capgo-unauthenticated-organization-enumeration-and-billing-status-disclosure-via-supabase-rpc
