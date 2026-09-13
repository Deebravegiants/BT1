# [M] CVE-2025-27809

## Summary
Severity: Medium
Advisory: CVE-2025-27809
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-03-25
Source: https://osv.dev/vulnerability/CVE-2025-27809
Type: osv

## Details
Mbed TLS before 2.28.10 and 3.x before 3.6.3, on the client side, accepts servers that have trusted certificates for arbitrary hostnames unless the TLS client application calls mbedtls_ssl_set_hostname.

## References
- https://mastodon.social/@bagder/114219540623402700
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27809.json
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2025-03-1/
- https://nvd.nist.gov/vuln/detail/CVE-2025-27809
- https://github.com/Mbed-TLS/mbedtls/issues/466
- https://github.com/Mbed-TLS/mbedtls/releases
