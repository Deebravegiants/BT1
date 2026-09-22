# [M] Capgo - Unauthenticated Denial-of-Service via audit_logs RLS Policy

## Summary
Severity: Medium
Advisory: CVE-2026-56248
Aliases: GHSA-5vgv-rqj5-5748
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56248
Type: osv

## Details
Cap-go capgo (capgo-backend) before 12.128.12 contains an unauthenticated denial-of-service vulnerability arising from the audit_logs table's Row-Level Security (RLS) policy when accessed via the Supabase PostgREST API. Because the PostgreSQL query planner executes costly logic before RLS rejection, unfiltered queries to the public.audit_logs endpoint using the public anon key consistently trigger statement timeouts (PostgREST error 57014). Under concurrency, this exhausts database resources and causes cascading HTTP 500 failures on unrelated endpoints (e.g. /orgs), resulting in an application-layer denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56248.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-5vgv-rqj5-5748
- https://nvd.nist.gov/vuln/detail/CVE-2026-56248
- https://www.vulncheck.com/advisories/capgo-unauthenticated-denial-of-service-via-audit-logs-rls-policy
