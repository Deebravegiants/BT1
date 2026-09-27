# [C] CVE-2024-45158

## Summary
Severity: Critical
Advisory: CVE-2024-45158
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-05
Source: https://osv.dev/vulnerability/CVE-2024-45158
Type: osv

## Details
An issue was discovered in Mbed TLS 3.6 before 3.6.1. A stack buffer overflow in mbedtls_ecdsa_der_to_raw() and mbedtls_ecdsa_raw_to_der() can occur when the bits parameter is larger than the largest supported curve. In some configurations with PSA disabled, all values of bits are affected. (This never happens in internal library calls, but can affect applications that call these functions directly.)

## References
- https://github.com/Mbed-TLS/mbedtls/releases/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45158.json
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2024-08-2/
- https://nvd.nist.gov/vuln/detail/CVE-2024-45158
