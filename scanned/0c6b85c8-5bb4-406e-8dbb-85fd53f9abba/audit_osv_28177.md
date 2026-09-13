# [M] CVE-2024-28836

## Summary
Severity: Medium
Advisory: CVE-2024-28836
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-28836
Type: osv

## Details
An issue was discovered in Mbed TLS 3.5.x before 3.6.0. When negotiating the TLS version on the server side, it can fall back to the TLS 1.2 implementation of the protocol if it is disabled. If the TLS 1.2 implementation was disabled at build time, a TLS 1.2 client could put a TLS 1.3-only server into an infinite loop processing a TLS 1.2 ClientHello, resulting in a denial of service. If the TLS 1.2 implementation was disabled at runtime, a TLS 1.2 client can successfully establish a TLS 1.2 connection with the server.

## References
- https://github.com/Mbed-TLS/mbedtls/releases/tag/v3.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28836.json
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2024-28836
