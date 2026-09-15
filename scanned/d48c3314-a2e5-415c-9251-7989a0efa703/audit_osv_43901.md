# [C] ArcadeDB before 26.8.1 Authentication Bypass via Async Command

## Summary
Severity: Critical
Advisory: CVE-2026-75851
Aliases: GHSA-5j4x-3jfw-8xv3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75851
Type: osv

## Details
ArcadeDB server (com.arcadedb:arcadedb-server) in versions 26.7.3 and earlier fails to propagate the authenticated principal to asynchronous command worker threads. When an HTTP command is submitted with awaitResponse:false, it executes on an async worker whose DatabaseContext has no bound user, causing the scripting authorization gate to become a no-op. A user with only read access to a single database can submit an asynchronous JavaScript (language=js) command via the /api/v1/command endpoint to run code with unrestricted host access (e.g., database.getSecurity().createUser) and create a server-wide administrator, escalating to full administrative control. Fixed in 26.8.1.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-5j4x-3jfw-8xv3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75851.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75851
- https://www.vulncheck.com/advisories/arcadedb-before-authentication-bypass-via-async-command
