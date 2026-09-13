# [C] CVE-2026-34877

## Summary
Severity: Critical
Advisory: CVE-2026-34877
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34877
Type: osv

## Details
An issue was discovered in Mbed TLS versions from 2.19.0 up to 3.6.5, Mbed TLS 4.0.0. Insufficient protection of serialized SSL context or session structures allows an attacker who can modify the serialized structures to induce memory corruption, leading to arbitrary code execution. This is caused by Incorrect Use of Privileged APIs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34877.json
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/
- https://mbed-tls.readthedocs.io/en/latest/security-advisories/mbedtls-security-advisory-2026-03-serialized-data/
- https://nvd.nist.gov/vuln/detail/CVE-2026-34877
