# [M] CVE-2021-44718

## Summary
Severity: Medium
Advisory: CVE-2021-44718
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-02
Source: https://osv.dev/vulnerability/CVE-2021-44718
Type: osv

## Details
wolfSSL through 5.0.0 allows an attacker to cause a denial of service and infinite loop in the client component by sending crafted traffic from a Machine-in-the-Middle (MITM) position. The root cause is that the client module accepts TLS messages that normally are only sent to TLS servers.

## References
- https://github.com/wolfSSL/wolfssl/releases
- https://www.wolfssl.com/docs/security-vulnerabilities/
