# [M] Capgo - Unauthenticated Organization Existence Enumeration via rescind_invitation RPC

## Summary
Severity: Medium
Advisory: CVE-2026-56339
Aliases: GHSA-8432-3cgm-vw5j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-56339
Type: osv

## Details
Capgo (Cap-go/capgo) before 12.128.2 contains an information disclosure vulnerability in the Supabase PostgREST SECURITY DEFINER RPC function public.rescind_invitation that allows unauthenticated attackers to enumerate organization existence. The function returns distinct error messages (NO_ORG vs NO_RIGHTS) when called with only a publishable API key, enabling attackers to discover valid organization IDs and increase the attack surface for targeted phishing or social engineering campaigns.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56339.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-8432-3cgm-vw5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-56339
- https://www.vulncheck.com/advisories/capgo-unauthenticated-organization-existence-enumeration-via-rescind-invitation-rpc
