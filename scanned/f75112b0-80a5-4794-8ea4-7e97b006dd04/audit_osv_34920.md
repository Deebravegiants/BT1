# [M] CVE-2025-66442

## Summary
Severity: Medium
Advisory: CVE-2025-66442
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2025-66442
Type: osv

## Details
In Mbed TLS through 4.0.0, there is a compiler-induced timing side channel (in RSA and CBC/ECB decryption) that only occurs with LLVM's select-optimize feature. TF-PSA-Crypto through 1.0.0 is also affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66442.json
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-compiler-induced-constant-time-violations/
- https://nvd.nist.gov/vuln/detail/CVE-2025-66442
- https://github.com/Mbed-TLS/TF-PSA-Crypto/releases
- https://github.com/Mbed-TLS/mbedtls/releases
