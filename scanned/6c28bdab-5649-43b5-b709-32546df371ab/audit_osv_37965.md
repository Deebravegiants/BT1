# [M] Coolify Settings/Updates Livewire component missing instance administrator authorization

## Summary
Severity: Medium
Advisory: CVE-2026-34050
Aliases: GHSA-c339-w3cq-2rjr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-34050
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, the Settings/Updates Livewire component does not check isInstanceAdmin in its mount method, allowing non-admin users to access the Updates settings page and potentially modify auto-update settings or trigger update checks. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34050.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-c339-w3cq-2rjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34050
- https://github.com/coollabsio/coolify/commit/0fed553207383f384b93cba24d28122065fa67d5
- https://github.com/coollabsio/coolify/pull/9206
