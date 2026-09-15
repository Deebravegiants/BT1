# [M] Domain Name Validation Bypass with Apple Native Certificate Validation

## Summary
Severity: Medium
Advisory: CVE-2025-7395
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/AU:Y/V:D/U:Red)
Published: 2025-07-18
Source: https://osv.dev/vulnerability/CVE-2025-7395
Type: osv

## Details
A certificate verification error in wolfSSL when building with the WOLFSSL_SYS_CA_CERTS and WOLFSSL_APPLE_NATIVE_CERT_VALIDATION options results in the wolfSSL
 client failing to properly verify the server certificate's domain name,
 allowing any certificate issued by a trusted CA to be accepted regardless of the hostname.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7395.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-7395
- http://github.com/wolfssl/wolfssl.git
- https://github.com/wolfSSL/wolfssl
