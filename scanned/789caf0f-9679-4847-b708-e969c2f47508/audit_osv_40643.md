# [M] OpenChamber 1.11.7 Unauthenticated DoS via /api/system/shutdown

## Summary
Severity: Medium
Advisory: CVE-2026-53977
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-53977
Type: osv

## Details
OpenChamber 1.11.7 contains an authentication bypass vulnerability that allows unauthenticated remote attackers to terminate the server process by sending a POST request to the /api/system/shutdown endpoint, which is registered before the authentication middleware in the Express route handler chain. Attackers can exploit the route registration order in bootstrap-runtime.js to reach the shutdown handler before auth middleware executes, causing denial of service to all active AI coding sessions and locking out legitimate remote users regardless of whether UI_PASSWORD is configured.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53977.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53977
- https://www.vulncheck.com/advisories/openchamber-unauthenticated-dos-via-api-system-shutdown
- https://github.com/openchamber/openchamber/commit/f1b9506132faf6c564a2694c7f33b94421a49b4a
- https://github.com/openchamber/openchamber
