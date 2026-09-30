# [M] TinyWeb has Unbounded Content-Length Memory Exhaustion (DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-27633
Aliases: GHSA-992w-gmcm-fmgr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27633
Type: osv

## Details
TinyWeb is a web server (HTTP, HTTPS) written in Delphi for Win32. Versions prior to version 2.02 have a Denial of Service (DoS) vulnerability via memory exhaustion. Unauthenticated remote attackers can send an HTTP POST request to the server with an exceptionally large `Content-Length` header (e.g., `2147483647`). The server continuously allocates memory for the request body (`EntityBody`) while streaming the payload without enforcing any maximum limit, leading to all available memory being consumed and causing the server to crash. Anyone hosting services using TinyWeb is impacted. Version 2.02 fixes the issue. The patch introduces a `CMaxEntityBodySize` limit (set to 10MB) for the maximum size of accepted payloads. As a temporary workaround if upgrading is not immediately possible, consider placing the server behind a Web Application Firewall (WAF) or reverse proxy (like nginx or Cloudflare) configured to explicitly limit the maximum allowed HTTP request body size (e.g., `client_max_body_size` in nginx).

## References
- https://www.masiutin.net/tinyweb-cve-2026-27633.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27633.json
- https://github.com/maximmasiutin/TinyWeb/security/advisories/GHSA-992w-gmcm-fmgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27633
- https://github.com/maximmasiutin/TinyWeb/commit/1cb5a1d
