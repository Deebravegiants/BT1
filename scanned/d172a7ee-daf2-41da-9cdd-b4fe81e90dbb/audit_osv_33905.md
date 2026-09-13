# [M] CVE-2025-52497

## Summary
Severity: Medium
Advisory: CVE-2025-52497
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-52497
Type: osv

## Details
Mbed TLS before 3.6.4 has a PEM parsing one-byte heap-based buffer underflow, in mbedtls_pem_read_buffer and two mbedtls_pk_parse functions, via untrusted PEM input.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00013.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52497.json
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2025-06-2.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-52497
