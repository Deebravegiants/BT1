# [M] Capgo - Unauthenticated Cross-Tenant Billing Log Tampering via public.record_build_time RPC

## Summary
Severity: Medium
Advisory: CVE-2026-56082
Aliases: GHSA-42xj-3h9w-26h5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-56082
Type: osv

## Details
Capgo (Cap-go/capgo) before 12.128.2 contains an improper access control vulnerability in the SECURITY DEFINER PostgREST RPC function public.record_build_time, which is granted to the anon role and callable with only the public Supabase publishable (sb_publishable_*) anon key. An unauthenticated attacker can insert rows into public.build_logs for arbitrary organizations and, because the function uses ON CONFLICT (build_id, org_id) DO UPDATE, can overwrite existing usage/billing records by reusing the same build_id for a target org. This enables cross-tenant tampering of billing build logs and financial-impact denial of service by inflating billable build time.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56082.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-42xj-3h9w-26h5
- https://nvd.nist.gov/vuln/detail/CVE-2026-56082
- https://www.vulncheck.com/advisories/supabase-unauthenticated-cross-tenant-billing-log-tampering-via-public-record-build-time-rpc
