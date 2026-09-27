# [H] Timescale pg-aiguide through 0.5.0 DNS Rebinding via Disabled Host Header Allow-List

## Summary
Severity: High
Advisory: CVE-2026-81095
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81095
Type: osv

## Details
pg-aiguide started its MCP HTTP transport without enabling the host allow-list the underlying SDK provides. src/httpServer.ts called the shared httpServerFactory helper and never set the DNS-rebinding-protection option, so the transport accepted a request whatever host it named. A page in a browser could therefore point a name it controlled at the address the server was bound to and drive the locally reachable MCP server through the visitor's browser. The protection was already available in the packaged transport and simply not turned on, so updating the dependency alone would not have closed it. Version 0.5.1 passes the option explicitly.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81095.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81095
- https://www.vulncheck.com/advisories/timescale-pg-aiguide-through-0.5.0-dns-rebinding-via-disabled-host-header-allow-list
- https://github.com/timescale/pg-aiguide/pull/121
- https://github.com/timescale/pg-aiguide
