# [C] dbx: Unauthenticated arbitrary SQL execution in dbx-web (authentication fails open when no password is configured)

## Summary
Severity: Critical
Advisory: CVE-2026-55642
Aliases: GHSA-rqp4-8fxh-22vh
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-55642
Type: osv

## Details
dbx is a cross-platform database client for databases. Prior to 0.5.51, dbx-web auth_middleware in crates/dbx-web/src/auth.rs passes every protected request to the handler chain when password_hash is None. A fresh deployment reaches that state when DBX_PASSWORD is unset and no stored password exists, while crates/dbx-web/src/main.rs binds the service to 0.0.0.0 on port 4224 by default. An unauthenticated network attacker can call the /api/connection/connect and /api/query/execute routes to use configured database credentials and execute arbitrary SQL, allowing disclosure, modification, or destruction of data in connected databases. The desktop Tauri application is not affected because it binds only to loopback. This issue is fixed in version 0.5.51.

## References
- https://github.com/t8y2/dbx/releases/tag/v0.5.51
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55642.json
- https://github.com/t8y2/dbx/security/advisories/GHSA-rqp4-8fxh-22vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-55642
- https://github.com/t8y2/dbx/issues/2887
- https://github.com/t8y2/dbx/commit/fb919efe0a62869631f49242d1f4fe8d41718c2a
