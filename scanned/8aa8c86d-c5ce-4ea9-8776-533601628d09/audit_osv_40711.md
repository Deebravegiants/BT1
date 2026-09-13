# [H] Missing Authentication for Critical Function in wallos

## Summary
Severity: High
Advisory: CVE-2026-54598
Aliases: GHSA-fgfx-rc43-4rr7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-54598
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.9.4, endpoints/db/migrate.php executes database schema migrations when called over HTTP with zero authentication. Any unauthenticated attacker can trigger pending migration files against the live SQLite database. This issue has been patched in version 4.9.4.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.9.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54598.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-fgfx-rc43-4rr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-54598
