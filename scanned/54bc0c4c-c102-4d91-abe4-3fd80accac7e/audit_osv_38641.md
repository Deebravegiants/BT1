# [C] Jellystat has SQL Injection that leads to to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-41167
Aliases: GHSA-fj7c-2p5q-g56m
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41167
Type: osv

## Details
Jellystat is a free and open source Statistics App for Jellyfin. Prior to version 1.1.10, multiple API endpoints in Jellystat build SQL queries by interpolating unsanitized request-body fields directly into raw SQL strings. An authenticated user can inject arbitrary SQL via `POST /api/getUserDetails` and `POST /api/getLibrary`, enabling full read of any table in the database - including `app_config`, which stores the Jellystat admin credentials, the Jellyfin API key, and the Jellyfin host URL. Because the vulnerable call site dispatches via `node-postgres`'s simple query protocol (no parameter array is passed), stacked queries are allowed, which escalates the injection from data disclosure to arbitrary command execution on the PostgreSQL host via `COPY ... TO PROGRAM`. Under the role shipped by the project's `docker-compose.yml` (a PostgreSQL superuser), no additional privileges are required to reach the RCE primitive. Version 1.1.10 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41167.json
- https://github.com/CyferShepard/Jellystat/security/advisories/GHSA-fj7c-2p5q-g56m
- https://nvd.nist.gov/vuln/detail/CVE-2026-41167
- https://github.com/CyferShepard/Jellystat/commit/735fe7c6eb0e3e34e92a8a82fd21914d76693665
