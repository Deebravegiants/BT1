# [H] Spring Cloud Commons no allow list for writable env actuator endpoint

## Summary
Severity: High
Advisory: CVE-2026-59284
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:L)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59284
Type: osv

## Details
There is no allow list for property keys when Spring Cloud Commons writable /actuator/env is enabled.
Spring Cloud Commons 5.0.0 - 5.0.2
Spring Cloud Commons 4.3.0 - 4.3.3
Spring Cloud Commons 4.0.0 - 4.2.6
Spring Cloud Commons 3.1.10 and earlier

## References
- https://spring.io/security/cve-2026-59284
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59284.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59284
