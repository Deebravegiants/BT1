# [C] Capgo - Cross-Organization App Takeover via Mismatched org_id and app_id in /private/role_bindings

## Summary
Severity: Critical
Advisory: CVE-2026-56222
Aliases: GHSA-5r52-m8r9-7f8x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56222
Type: osv

## Details
Capgo before 12.128.2 contains an authorization bypass vulnerability in POST /private/role_bindings that fails to verify app_id ownership during app-scoped role binding creation. An attacker with administrative privileges in one organization can create role bindings targeting applications owned by other organizations, enabling unauthorized read and modification of victim applications.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56222.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-5r52-m8r9-7f8x
- https://nvd.nist.gov/vuln/detail/CVE-2026-56222
- https://www.vulncheck.com/advisories/capgo-cross-organization-app-takeover-via-mismatched-org-id-and-app-id-in-private-role-bindings
