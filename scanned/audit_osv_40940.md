# [M] Supabase Capgo - Unauthenticated Cross-Tenant Build-Time Accounting Poisoning via record_build_time RPC

## Summary
Severity: Medium
Advisory: CVE-2026-56245
Aliases: GHSA-42f8-v563-5763
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56245
Type: osv

## Details
Supabase Capgo before 12.128.2 contains an authorization bypass vulnerability in the SECURITY DEFINER record_build_time RPC function that allows unauthenticated attackers to insert arbitrary build-time records. Attackers can exploit this by calling POST /rest/v1/rpc/record_build_time with a public API key to poison billing and quota data for any organization, enabling resource exhaustion and cross-tenant billing manipulation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56245.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-42f8-v563-5763
- https://nvd.nist.gov/vuln/detail/CVE-2026-56245
- https://www.vulncheck.com/advisories/supabase-capgo-unauthenticated-cross-tenant-build-time-accounting-poisoning-via-record-build-time-rpc
