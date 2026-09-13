# [M] Heap-buffer over-read with WOLFSSL_CALLBACKS

## Summary
Severity: Medium
Advisory: CVE-2023-6936
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2023-6936
Type: osv

## Details
In wolfSSL prior to 5.6.6, if callback functions are enabled (via the WOLFSSL_CALLBACKS flag), then a malicious TLS client or network attacker can trigger a buffer over-read on the heap of 5 bytes (WOLFSSL_CALLBACKS is only intended for debugging).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6936.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6936
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/wolfSSL/wolfssl/pull/6949/
- https://github.com/wolfSSL/wolfssl
