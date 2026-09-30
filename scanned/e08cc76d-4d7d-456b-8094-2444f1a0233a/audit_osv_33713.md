# [M] CVE-2025-49087

## Summary
Severity: Medium
Advisory: CVE-2025-49087
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2025-07-20
Source: https://osv.dev/vulnerability/CVE-2025-49087
Type: osv

## Details
In Mbed TLS 3.6.1 through 3.6.3 before 3.6.4, a timing discrepancy in block cipher padding removal allows an attacker to recover the plaintext when PKCS#7 padding mode is used.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49087.json
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2025-06-5.md
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2025-49087
