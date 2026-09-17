# [M] Static Web Server: Authentication bypass on /metrics endpoint when --basic-auth is enabled

## Summary
Severity: Medium
Advisory: CVE-2026-75601
Aliases: GHSA-97q6-jph8-rxgm
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-75601
Type: osv

## Details
Static Web Server (SWS) is a production-ready web server suitable for static web files or assets. Through 2.43.0, instances with both basic-auth and metrics features enabled process the /metrics endpoint before the basic-auth check in src/handler.rs, allowing an unauthenticated remote attacker to retrieve Prometheus metrics that disclose virtual host names, request volumes, error rates, latency distributions, and active connections. This issue is fixed in version 2.44.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75601.json
- https://github.com/static-web-server/static-web-server/security/advisories/GHSA-97q6-jph8-rxgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-75601
- https://github.com/static-web-server/static-web-server/commit/a51444c81abb7d417fd931f5df58227dd04192f5
