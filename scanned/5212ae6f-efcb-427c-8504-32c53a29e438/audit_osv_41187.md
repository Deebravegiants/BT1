# [H] Ocelot - IP Allow/Block List Bypass for WebSocket Upgrade Requests

## Summary
Severity: High
Advisory: CVE-2026-58172
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58172
Type: osv

## Details
Ocelot through 24.1.0, fixed in commit f156fd4, contains a security control bypass vulnerability that allows denied clients to circumvent IP-based access restrictions by sending WebSocket upgrade requests. The WebSocket upgrade pipeline branch configured via MapWhen in OcelotPipelineExtensions.cs omits SecurityMiddleware, causing requests from blocked IP addresses to be proxied to downstream services without enforcement of the configured allow/block list.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58172.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58172
- https://www.vulncheck.com/advisories/ocelot-ip-allow-block-list-bypass-for-websocket-upgrade-requests
- https://github.com/ThreeMammals/Ocelot/pull/2406
- https://github.com/ThreeMammals/Ocelot/commit/f156fd4017ca25025fffdad8ec56c1d657dfb402
- https://github.com/ThreeMammals/Ocelot
- https://github.com/ThreeMammals/Ocelot/issues/2403
