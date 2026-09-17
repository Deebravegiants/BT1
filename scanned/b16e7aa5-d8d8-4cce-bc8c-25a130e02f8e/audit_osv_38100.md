# [H] Coolify: Authenticated Remote Code Execution in GetLogs Livewire Component

## Summary
Severity: High
Advisory: CVE-2026-34599
Aliases: GHSA-q9j6-xcvx-px63
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-34599
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, there is an authenticated command injection vulnerability in the GetLogs Livewire component which allows users with team membership (lowest privilege member role) to execute arbitrary commands as root on managed servers. The $container Livewire public property is interpolated directly into shell commands (docker logs, docker service logs) without sanitization, and can be modified by any client via the Livewire wire protocol because it lacks the #[Locked] attribute. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34599.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-q9j6-xcvx-px63
- https://nvd.nist.gov/vuln/detail/CVE-2026-34599
- https://github.com/coollabsio/coolify/commit/f267a28cb2badc7e712c4592af4d79d090fe5063
- https://github.com/coollabsio/coolify/pull/9229
