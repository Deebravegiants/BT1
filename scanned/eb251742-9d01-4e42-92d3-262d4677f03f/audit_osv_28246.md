# [C] CVE-2024-30166

## Summary
Severity: Critical
Advisory: CVE-2024-30166
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-30166
Type: osv

## Details
In Mbed TLS 3.3.0 through 3.5.2 before 3.6.0, a malicious client can cause information disclosure or a denial of service because of a stack buffer over-read (of less than 256 bytes) in a TLS 1.3 server via a TLS 3.1 ClientHello.

## References
- https://github.com/Mbed-TLS/mbedtls/releases/tag/v3.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30166.json
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2024-30166
