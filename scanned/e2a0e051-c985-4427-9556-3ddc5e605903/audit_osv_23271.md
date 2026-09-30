# [C] CVE-2022-46393

## Summary
Severity: Critical
Advisory: CVE-2022-46393
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-15
Source: https://osv.dev/vulnerability/CVE-2022-46393
Type: osv

## Details
An issue was discovered in Mbed TLS before 2.28.2 and 3.x before 3.3.0. There is a potential heap-based buffer overflow and heap-based buffer over-read in DTLS if MBEDTLS_SSL_DTLS_CONNECTION_ID is enabled and MBEDTLS_SSL_CID_IN_LEN_MAX > 2 * MBEDTLS_SSL_CID_OUT_LEN_MAX.

## References
- https://github.com/Mbed-TLS/mbedtls/releases/tag/v2.28.2
- https://github.com/Mbed-TLS/mbedtls/releases/tag/v3.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46393.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4BR7ZCVKLPGCOEEALUHZMFHXQHR6S4QL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6XMKJ5IMJEPXYAHHU56Z4P2FSYIEAESB/
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2022-46393
