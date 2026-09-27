# [M] Coolify: Cross-tenant activity log disclosure via unlocked Livewire property in ActivityMonitor

## Summary
Severity: Medium
Advisory: CVE-2026-34167
Aliases: GHSA-962v-gxmw-56hc
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-34167
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, the ActivityMonitor Livewire component exposes a public $activityId property without Livewire's #[Locked] attribute. It loads activities via Activity::find($this->activityId) with no authorization or team scoping. Activity IDs are auto-incrementing integers. Any authenticated user can enumerate activity records across all teams and read the full command output from remote SSH processes, which may include secrets, configuration files, and infrastructure details. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34167.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-962v-gxmw-56hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-34167
- https://github.com/coollabsio/coolify/commit/2729dffb3e30167c1ffd642357b7e0bb99b7d180
- https://github.com/coollabsio/coolify/pull/9189
