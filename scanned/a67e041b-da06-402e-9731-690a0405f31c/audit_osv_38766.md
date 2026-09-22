# [H] Coolify: PostgreSQL Healthcheck Command Injection Allows Root Code Execution in Container

## Summary
Severity: High
Advisory: CVE-2026-42153
Aliases: GHSA-gvc4-f276-r88p
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-42153
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.474, PostgreSQL healthcheck command generation used attacker-controlled database settings (postgres_user and postgres_db) in shell-form commands, allowing an authenticated user to inject commands executed in the database container. This issue is fixed in version 4.0.0-beta.474.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.474
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42153.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-gvc4-f276-r88p
- https://nvd.nist.gov/vuln/detail/CVE-2026-42153
- https://github.com/coollabsio/coolify/commit/b74f54302b1a857c22c55fe1210d700859b0b3df
- https://github.com/coollabsio/coolify/pull/9674
