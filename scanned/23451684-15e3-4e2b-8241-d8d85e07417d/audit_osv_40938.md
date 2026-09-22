# [H] Capgo - Hashed API Key Enforcement Bypass via PostgREST/RLS Plane

## Summary
Severity: High
Advisory: CVE-2026-56243
Aliases: GHSA-6g74-8cpq-g2c8
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56243
Type: osv

## Details
Capgo before 12.128.2 contains a security control bypass vulnerability where the PostgREST/RLS plane accepts plaintext API keys through the capgkey header despite enforce_hashed_api_keys being enabled. Attackers can bypass org-level hashed-key enforcement by sending plaintext API keys directly to the PostgREST/RLS plane to access protected resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56243.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-6g74-8cpq-g2c8
- https://nvd.nist.gov/vuln/detail/CVE-2026-56243
- https://www.vulncheck.com/advisories/capgo-hashed-api-key-enforcement-bypass-via-postgrest-rls-plane
