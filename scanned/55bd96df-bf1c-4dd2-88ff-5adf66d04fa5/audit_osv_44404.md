# [M] CVE-2026-8209

## Summary
Severity: Medium
Advisory: CVE-2026-8209
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-05-09
Source: https://osv.dev/vulnerability/CVE-2026-8209
Type: osv

## Details
Gibbon versions before v30.0.01 are affected by a path traversal vulnerability resulting in DOS by attempting extraction of web application PHP files, failed .zip extraction results in deletion of the file and a DOS condition. Successful exploitation requires Teacher or higher privileges. Exploitation could result in loss of availability of the web application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8209.json
- https://github.com/GibbonEdu/core/releases/tag/v30.0.01
- https://nvd.nist.gov/vuln/detail/CVE-2026-8209
- https://projectblack.io/blog/gibbon-v30-authenticated-sql-injection-and-rce/#denial-of-service-via-path-traversal
