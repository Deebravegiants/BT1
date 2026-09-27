# [M] Capgo - Unauthenticated Organization Data Disclosure via get_orgs_v6 RPC

## Summary
Severity: Medium
Advisory: CVE-2026-56226
Aliases: GHSA-m7mm-35v3-82f4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56226
Type: osv

## Details
Capgo (Cap-go/capgo) before 12.128.2 exposes the Supabase PostgREST RPC function public.get_orgs_v6(userid uuid), which is SECURITY DEFINER and granted to the anon role, allowing unauthenticated access. Because the function accepts a caller-supplied user UUID without verifying it matches the authenticated user, an attacker using only the public publishable API key can query POST /rest/v1/rpc/get_orgs_v6 with an arbitrary user UUID to retrieve that user's organization membership, roles, subscription/trial metadata, and management_email (PII).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56226.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-m7mm-35v3-82f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-56226
- https://www.vulncheck.com/advisories/capgo-unauthenticated-organization-data-disclosure-via-get-orgs-v6-rpc
