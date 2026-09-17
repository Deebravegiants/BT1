# [M] Capgo - Privilege Escalation via SECURITY DEFINER Function apply_usage_overage

## Summary
Severity: Medium
Advisory: CVE-2026-56239
Aliases: GHSA-qq85-vjrq-m75g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2026-56239
Type: osv

## Details
Capgo before 12.128.2 contains a potential privilege escalation vulnerability in the public.apply_usage_overage SECURITY DEFINER function, which performs sensitive billing operations without enforcing internal authorization checks (no validation of auth.uid(), org membership, or check_min_rights). Because the function runs with the owner's privileges, it bypasses Row Level Security. If EXECUTE permission is available to the authenticated or anon roles (explicitly or via default privileges), an authenticated user could invoke it via Supabase RPC to manipulate billing data for arbitrary organizations, including unauthorized credit depletion and fraudulent overage event insertion.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56239.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-qq85-vjrq-m75g
- https://nvd.nist.gov/vuln/detail/CVE-2026-56239
- https://www.vulncheck.com/advisories/capgo-privilege-escalation-via-security-definer-function-apply-usage-overage
