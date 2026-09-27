# [M] CVE-2025-27810

## Summary
Severity: Medium
Advisory: CVE-2025-27810
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-03-25
Source: https://osv.dev/vulnerability/CVE-2025-27810
Type: osv

## Details
Mbed TLS before 2.28.10 and 3.x before 3.6.3, in some cases of failed memory allocation or hardware errors, uses uninitialized stack memory to compose the TLS Finished message, potentially leading to authentication bypasses such as replays.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27810.json
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2025-03-2/
- https://nvd.nist.gov/vuln/detail/CVE-2025-27810
- https://github.com/Mbed-TLS/mbedtls/releases
