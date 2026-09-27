# [M] CVE-2025-65670

## Summary
Severity: Medium
Advisory: CVE-2025-65670
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-65670
Type: osv

## Details
An Insecure Direct Object Reference (IDOR) in classroomio 0.1.13 allows students to access sensitive admin/teacher endpoints by manipulating course IDs in URLs, resulting in unauthorized disclosure of sensitive course, admin, and student data. The leak occurs momentarily before the system reverts to a normal state restricting access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65670.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65670
- https://github.com/Rivek619/CVE-2025-65670
- https://github.com/classroomio/classroomio
