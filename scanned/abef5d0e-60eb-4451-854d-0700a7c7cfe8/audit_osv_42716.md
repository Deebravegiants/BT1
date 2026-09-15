# [M] boringproxy 0.10.0 Resource Exhaustion DoS via GET /loading endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-70616
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-70616
Type: osv

## Details
boringproxy through 0.10.0 contains a resource exhaustion vulnerability that allows any authenticated user to permanently exhaust server file descriptors, goroutines, and memory by sending requests to the GET /loading endpoint with attacker-supplied id query parameter values. Because the handler performs no map-lookup validity check and receives on a nil channel that blocks forever, with no timeout, no context cancellation, and no server-side reclamation due to absent HTTP server timeouts, each malicious request permanently holds one goroutine, one file descriptor, and approximately 50 kB of memory until the server's file descriptor limit is reached and listener Accept calls fail, halting all tunnel traffic forwarding for all users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70616.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70616
- https://www.vulncheck.com/advisories/boringproxy-resource-exhaustion-dos-via-get-loading-endpoint
- https://github.com/boringproxy/boringproxy
- https://github.com/theopaid/Denial-Of-Service-Through-Unbounded-Resource-Consumption-In-Request-Handler-boringproxy-/blob/master/README.md
