# [C] CVE-2024-45159

## Summary
Severity: Critical
Advisory: CVE-2024-45159
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-05
Source: https://osv.dev/vulnerability/CVE-2024-45159
Type: osv

## Details
An issue was discovered in Mbed TLS 3.x before 3.6.1. With TLS 1.3, when a server enables optional authentication of the client, if the client-provided certificate does not have appropriate values in if keyUsage or extKeyUsage extensions, then the return value of mbedtls_ssl_get_verify_result() would incorrectly have the MBEDTLS_X509_BADCERT_KEY_USAGE and MBEDTLS_X509_BADCERT_KEY_USAGE bits clear. As a result, an attacker that had a certificate valid for uses other than TLS client authentication would nonetheless be able to use it for TLS client authentication. Only TLS 1.3 servers were affected, and only with optional authentication (with required authentication, the handshake would be aborted with a fatal alert).

## References
- https://github.com/Mbed-TLS/mbedtls/releases/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45159.json
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2024-08-3/
- https://nvd.nist.gov/vuln/detail/CVE-2024-45159
