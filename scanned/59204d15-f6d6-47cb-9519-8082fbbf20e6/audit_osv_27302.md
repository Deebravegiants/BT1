# [M] Fault Injection of RSA encryption in WolfCrypt

## Summary
Severity: Medium
Advisory: CVE-2024-1545
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:L)
Published: 2024-08-29
Source: https://osv.dev/vulnerability/CVE-2024-1545
Type: osv

## Details
Fault Injection vulnerability in RsaPrivateDecryption function in wolfssl/wolfcrypt/src/rsa.c in WolfSSL wolfssl5.6.6 on Linux/Windows allows remote attacker co-resides in the same system with a victim process to disclose information and escalate privileges via Rowhammer fault injection to the RsaKey structure.

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v5.7.0-stable
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1545.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1545
- https://github.com/wolfSSL/wolfssl/pull/7167
- https://github.com/wolfSSL/wolfssl
