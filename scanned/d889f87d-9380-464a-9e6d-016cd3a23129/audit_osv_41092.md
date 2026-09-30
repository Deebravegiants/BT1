# [C] Coolify Cross-Team IDOR: Livewire Components Accept Unscoped server_id and destination_uuid — Deploy to Other Teams' Servers

## Summary
Severity: Critical
Advisory: CVE-2026-57498
Aliases: GHSA-725v-f5gh-22q9
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57498
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.474, Coolify's API controllers consistently validate server ownership with Server::whereTeamId($teamId) before any operation. However, multiple Livewire web UI components accept server_id and destination_uuid from URL query parameters without any team ownership validation, allowing cross-team resource deployment. This vulnerability is fixed in 4.0.0-beta.474.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57498.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-725v-f5gh-22q9
- https://nvd.nist.gov/vuln/detail/CVE-2026-57498
