# [M] CVE-2025-54764

## Summary
Severity: Medium
Advisory: CVE-2025-54764
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-20
Source: https://osv.dev/vulnerability/CVE-2025-54764
Type: osv

## Details
Mbed TLS before 3.6.5 allows a local timing attack against certain RSA operations, and direct calls to mbedtls_mpi_mod_inv or mbedtls_mpi_gcd.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54764.json
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2025-10-ssbleed-mstep/
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2025-54764
