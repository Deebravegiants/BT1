# [M] Coolify: Cross-team application domain enumeration via domains_by_server endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-27956
Aliases: GHSA-9x6p-29p3-h466
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-27956
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.464, `GET /api/v1/servers/{server_uuid}/domains?uuid={app_uuid}` bypasses team scoping when the optional uuid query parameter is provided. Any authenticated API user can enumerate domain names (FQDNs) of applications belonging to other teams. This vulnerability is fixed in 4.0.0-beta.464.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27956.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-9x6p-29p3-h466
- https://nvd.nist.gov/vuln/detail/CVE-2026-27956
