# [M] CVE-2024-28755

## Summary
Severity: Medium
Advisory: CVE-2024-28755
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-28755
Type: osv

## Details
An issue was discovered in Mbed TLS 3.5.x before 3.6.0. When an SSL context was reset with the mbedtls_ssl_session_reset() API, the maximum TLS version to be negotiated was not restored to the configured one. An attacker was able to prevent an Mbed TLS server from establishing any TLS 1.3 connection, potentially resulting in a Denial of Service or forced version downgrade from TLS 1.3 to TLS 1.2.

## References
- https://github.com/Mbed-TLS/mbedtls/releases/tag/v3.6.0
- https://github.com/hey3e
- https://hey3e.github.io
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28755.json
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2024-28755
