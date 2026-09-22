# [H] live information startup mode is vulnerable for remote code execution

## Summary
Severity: High
Advisory: CVE-2026-47858
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-47858
Type: osv

## Details
Starting Spring Boot applications in the Spring Tools with the live information mode enabled makes the running application vulnerable against JMX-based remote code execution.
Affected Spring Products and Versions:
Spring Tools for Eclipse: 5.2.0 and earlier
Spring Tools for VSCode / Cursor / Theia: 2.2.0 and earlier

## References
- https://spring.io/security/cve-2026-47858
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47858.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47858
