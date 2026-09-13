# [H] CVE-2025-52496

## Summary
Severity: High
Advisory: CVE-2025-52496
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-52496
Type: osv

## Details
Mbed TLS before 3.6.4 has a race condition in AESNI detection if certain compiler optimizations occur. An attacker may be able to extract an AES key from a multithreaded program, or perform a GCM forgery.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00013.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52496.json
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2025-06-1.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-52496
