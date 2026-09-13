# [C] Cross-Tenant Resource Cloning via Broken Object-Level Authorization in cloneTo()

## Summary
Severity: Critical
Advisory: CVE-2026-34037
Aliases: GHSA-ggrr-wrvr-x83v
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34037
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.464, the cloneTo() Livewire action in ResourceOperations.php authorizes the source resource but resolves destination resources with unscoped Eloquent lookups, allowing an authenticated user to clone resources into destinations owned by other teams and access cross-tenant resources. This issue is fixed in version 4.0.0-beta.464.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.464
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34037.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-ggrr-wrvr-x83v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34037
- https://github.com/coollabsio/coolify/commit/1759a1631cd63271ebf6caa250c6d93440eaa333
