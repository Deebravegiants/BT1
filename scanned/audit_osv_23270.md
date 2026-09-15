# [M] CVE-2022-46392

## Summary
Severity: Medium
Advisory: CVE-2022-46392
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-15
Source: https://osv.dev/vulnerability/CVE-2022-46392
Type: osv

## Details
An issue was discovered in Mbed TLS before 2.28.2 and 3.x before 3.3.0. An adversary with access to precise enough information about memory accesses (typically, an untrusted operating system attacking a secure enclave) can recover an RSA private key after observing the victim performing a single private-key operation, if the window size (MBEDTLS_MPI_WINDOW_SIZE) used for the exponentiation is 3 or smaller.

## References
- https://github.com/Mbed-TLS/mbedtls/releases/tag/v2.28.2
- https://github.com/Mbed-TLS/mbedtls/releases/tag/v3.3.0
- https://lists.debian.org/debian-lts-announce/2025/06/msg00034.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46392.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4BR7ZCVKLPGCOEEALUHZMFHXQHR6S4QL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6XMKJ5IMJEPXYAHHU56Z4P2FSYIEAESB/
- https://nvd.nist.gov/vuln/detail/CVE-2022-46392
