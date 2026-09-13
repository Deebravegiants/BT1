# [M] CVE-2025-48965

## Summary
Severity: Medium
Advisory: CVE-2025-48965
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2025-07-20
Source: https://osv.dev/vulnerability/CVE-2025-48965
Type: osv

## Details
Mbed TLS before 3.6.4 has a NULL pointer dereference because mbedtls_asn1_store_named_data can trigger conflicting data with val.p of NULL but val.len greater than zero.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00013.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48965.json
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2025-06-6.md
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2025-48965
