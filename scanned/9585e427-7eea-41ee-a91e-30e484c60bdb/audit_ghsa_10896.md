# [H] Netmaker Vulnerable to Denial of Service via Server Shutdown Endpoint

## Summary
Severity: High
Advisory: GHSA-rhr9-hgcm-x289
CVE: CVE-2026-29771
CWE: CWE-404
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-rhr9-hgcm-x289
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <1.2.0

## Details
The /api/server/shutdown endpoint allows termination of the Netmaker server process via syscall.SIGINT. This allows any user to repeatedly shut down the server, causing cyclic denial of service with approximately 3-second restart intervals.

## References
- https://github.com/gravitl/netmaker/security/advisories/GHSA-rhr9-hgcm-x289
- https://nvd.nist.gov/vuln/detail/CVE-2026-29771
- https://github.com/gravitl/netmaker
