# [M] TinyWeb vulnerable to Remote Denial of Service via Thread/Connection Exhaustion (Slowloris)

## Summary
Severity: Medium
Advisory: CVE-2026-27630
Aliases: GHSA-ccv5-8948-c99c
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27630
Type: osv

## Details
TinyWeb is a web server (HTTP, HTTPS) written in Delphi for Win32. Versions prior to version 2.02 are vulnerable to a Denial of Service (DoS) attack known as Slowloris. The server spawns a new OS thread for every incoming connection without enforcing a maximum concurrency limit or an appropriate request timeout. An unauthenticated remote attacker can exhaust server concurrency limits and memory by opening numerous connections and sending data exceptionally slowly (e.g. 1 byte every few minutes). Anyone hosting services using TinyWeb is impacted. Version 2.02 fixes the issue. The patch introduces a `CMaxConnections` limit (set to 512) and a `CConnectionTimeoutSecs` idle timeout (set to 30 seconds). As a temporary workaround if upgrading is not immediately possible, consider placing the server behind a robust reverse proxy or Web Application Firewall (WAF) such as nginx, HAProxy, or Cloudflare, configured to buffer incomplete requests and aggressively enforce connection limits and timeouts.

## References
- https://www.masiutin.net/tinyweb-cve-2026-27630.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27630.json
- https://github.com/maximmasiutin/TinyWeb/security/advisories/GHSA-ccv5-8948-c99c
- https://nvd.nist.gov/vuln/detail/CVE-2026-27630
- https://github.com/maximmasiutin/TinyWeb/commit/23268c8
