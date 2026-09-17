# [H] Error-based SQL Injection in Chamilo LMS

## Summary
Severity: High
Advisory: CVE-2025-50188
Aliases: GHSA-96j3-x45m-9q3r
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2025-50188
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.30, the application performs insufficient validation of data coming from the user from the GET value parameter with the following scripts: /plugin/vchamilo/views/syncparams.php and /plugin/vchamilo/ajax/service.php, which allows an attacker to perform an attack aimed at modifying the database query logic by injecting an arbitrary SQL statements. This issue has been patched in version 1.11.30.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50188.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-96j3-x45m-9q3r
- https://nvd.nist.gov/vuln/detail/CVE-2025-50188
- https://github.com/chamilo/chamilo-lms/commit/ef54cc0906a3caaa3e7ac9b640b044f03b1fe733
