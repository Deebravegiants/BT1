# [H] CVE-2023-52353

## Summary
Severity: High
Advisory: CVE-2023-52353
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-01-21
Source: https://osv.dev/vulnerability/CVE-2023-52353
Type: osv

## Details
An issue was discovered in Mbed TLS through 3.5.1. In mbedtls_ssl_session_reset, the maximum negotiable TLS version is mishandled. For example, if the last connection negotiated TLS 1.2, then 1.2 becomes the new maximum.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52353.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52353
- https://github.com/Mbed-TLS/mbedtls/issues/8654
