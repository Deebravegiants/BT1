# [H] Coolify: PostgreSQL Init Script Path Traversal Leads to Arbitrary File Write and Root RCE

## Summary
Severity: High
Advisory: CVE-2026-42200
Aliases: GHSA-mv4c-9x67-rrmv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-42200
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.474, PostgreSQL initialization script (generate_init_scripts() method in app/Actions/Database/StartPostgresql.php) filename handling did not sufficiently restrict paths, allowing an authenticated user to write files outside the intended directory and achieve command execution through database initialization. This issue is fixed in version 4.0.0-beta.474.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.474
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42200.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-mv4c-9x67-rrmv
- https://nvd.nist.gov/vuln/detail/CVE-2026-42200
- https://github.com/coollabsio/coolify/commit/1cf6c7d0aef8e0edb800ae43f44ded102397cb13
- https://github.com/coollabsio/coolify/pull/9681
