# [M] FreeRDP before 3.29.0 Denial of Service via RDPEI PDU

## Summary
Severity: Medium
Advisory: CVE-2026-67296
Aliases: GHSA-jm8r-22j6-4m4v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67296
Type: osv

## Details
FreeRDP before 3.29.0 contains a denial of service vulnerability in the RDPEI server channel handler that fails to validate maximum PDU body length before stream allocation. A malicious RDP client can send a header-only RDPEI message with a large declared body length to force excessive memory allocation on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67296.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-jm8r-22j6-4m4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-67296
- https://www.vulncheck.com/advisories/freerdp-before-denial-of-service-via-rdpei-pdu
