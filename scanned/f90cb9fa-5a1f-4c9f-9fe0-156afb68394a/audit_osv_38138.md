# [H] CVE-2026-34874

## Summary
Severity: High
Advisory: CVE-2026-34874
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-34874
Type: osv

## Details
An issue was discovered in Mbed TLS through 3.6.5 and 4.x through 4.0.0. There is a NULL pointer dereference in distinguished name parsing that allows an attacker to write to address 0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34874.json
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-null-pointer-dereference-x509/
- https://nvd.nist.gov/vuln/detail/CVE-2026-34874
