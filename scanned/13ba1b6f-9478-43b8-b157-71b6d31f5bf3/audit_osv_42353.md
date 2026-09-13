# [M] FreeRDP before 3.29.0 Resource Exhaustion via chunked HTTP response

## Summary
Severity: Medium
Advisory: CVE-2026-67297
Aliases: GHSA-2c6r-4pr4-9x8m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67297
Type: osv

## Details
FreeRDP before 3.29.0 fails to enforce the RESPONSE_SIZE_LIMIT when processing Transfer-Encoding: chunked HTTP responses in http_response_recv_body(). Attackers controlling a malicious RD Gateway endpoint can send oversized chunked response bodies to exhaust client memory resources without triggering the configured size limit.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67297.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-2c6r-4pr4-9x8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-67297
- https://www.vulncheck.com/advisories/freerdp-before-resource-exhaustion-via-chunked-http-response
