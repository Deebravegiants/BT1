# [M] Safe-error attack on TLS 1.3 Protocol

## Summary
Severity: Medium
Advisory: CVE-2024-5288
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-08-27
Source: https://osv.dev/vulnerability/CVE-2024-5288
Type: osv

## Details
An issue was discovered in wolfSSL before 5.7.0. A safe-error attack via Rowhammer, namely FAULT+PROBE, leads to ECDSA key disclosure. When WOLFSSL_CHECK_SIG_FAULTS is used in signing operations with private ECC keys,

such as in server-side TLS connections, the connection is halted if any fault occurs. The success rate in a certain amount of connection requests can be processed via an advanced technique for ECDSA key recovery.

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v5.7.2-stable
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5288.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5288
- https://github.com/wolfSSL/wolfssl
