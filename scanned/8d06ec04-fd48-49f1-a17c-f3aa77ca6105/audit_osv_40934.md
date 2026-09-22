# [M] Capgo - Unauthenticated Information Disclosure via PostgREST global_stats Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-56238
Aliases: GHSA-73rv-fpp7-r3r4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-12
Source: https://osv.dev/vulnerability/CVE-2026-56238
Type: osv

## Details
Capgo before 12.128.2 contains an information disclosure vulnerability in the Supabase PostgREST global_stats endpoint that allows unauthenticated attackers to read sensitive financial and operational metrics using only the public apikey. Remote attackers can query the /rest/v1/global_stats endpoint to expose MRR, total revenue, plan-tier revenue breakdown, customer counts, and operational telemetry.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56238.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-73rv-fpp7-r3r4
- https://nvd.nist.gov/vuln/detail/CVE-2026-56238
- https://www.vulncheck.com/advisories/capgo-unauthenticated-information-disclosure-via-postgrest-global-stats-endpoint
