# [C] Coolify: Missing authorization on terminal websocket bootstrap routes allows low-privileged members to execute commands on team servers

## Summary
Severity: Critical
Advisory: CVE-2026-34048
Aliases: GHSA-mw6q-2hmg-mhxv
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34048
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, terminal websocket bootstrap routes only check authentication and do not enforce terminal authorization, allowing a low-privileged team member to connect to terminal routes and execute commands on team servers. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34048.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-mw6q-2hmg-mhxv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34048
- https://github.com/coollabsio/coolify/commit/847166a3f89b7c80972fa0d2e5c754976f95b6ad
