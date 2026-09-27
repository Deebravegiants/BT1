# [M] CVE-2025-7394

## Summary
Severity: Medium
Advisory: CVE-2025-7394
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2025-07-18
Source: https://osv.dev/vulnerability/CVE-2025-7394
Type: osv

## Details
In the OpenSSL compatibility layer implementation, the function RAND_poll() was not behaving as expected and leading to the potential for predictable values returned from RAND_bytes() after fork() is called. This can lead to weak or predictable random numbers generated in applications that are both using RAND_bytes() and doing fork() operations. This only affects applications explicitly calling RAND_bytes() after fork() and does not affect any internal TLS operations. Although RAND_bytes() documentation in OpenSSL calls out not being safe for use with fork() without first calling RAND_poll(), an additional code change was also made in wolfSSL to make RAND_bytes() behave similar to OpenSSL after a fork() call without calling RAND_poll(). Now the Hash-DRBG used gets reseeded after detecting running in a new process. If making use of RAND_bytes() and calling fork() we recommend updating to the latest version of wolfSSL. Thanks to Per Allansson from Appgate for the report.

## References
- https://github.com/wolfSSL/wolfssl/blob/master/ChangeLog.md#wolfssl-release-582-july-17-2025
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7394.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-7394
- https://github.com/wolfssl/wolfssl
