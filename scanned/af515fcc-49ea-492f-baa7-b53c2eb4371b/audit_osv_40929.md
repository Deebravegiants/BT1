# [C] Capgo - Broken Object Level Authorization via x-limited-key-id Header

## Summary
Severity: Critical
Advisory: CVE-2026-56230
Aliases: GHSA-cppm-733w-hg86
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-56230
Type: osv

## Details
Capgo before 12.128.2 contains a broken object level authorization vulnerability in middlewareKey() that accepts the client-controlled x-limited-key-id header without validating ownership, allowing authenticated users to adopt cross-tenant limited keys. Attackers can supply another tenant's limited key ID to bypass authorization checks and access unauthorized cross-tenant resources across multiple API endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56230.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-cppm-733w-hg86
- https://nvd.nist.gov/vuln/detail/CVE-2026-56230
- https://www.vulncheck.com/advisories/capgo-broken-object-level-authorization-via-x-limited-key-id-header
