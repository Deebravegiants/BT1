# [H] Chamilo: OS Command Injection in /plugin/vchamilo/views/editinstance.php via POST main_database parameter

## Summary
Severity: High
Advisory: CVE-2025-50196
Aliases: GHSA-qfvp-xg47-m7m2
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2025-50196
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.30, there is an OS Command Injection vulnerability in /plugin/vchamilo/views/editinstance.php via the POST main_database parameter. This issue has been patched in version 1.11.30.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50196.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-qfvp-xg47-m7m2
- https://nvd.nist.gov/vuln/detail/CVE-2025-50196
- https://github.com/chamilo/chamilo-lms/commit/afdbd4bb9a9ea17b7740559dd4e05aa13b16480d
- https://github.com/chamilo/chamilo-lms/commit/e343c764493b457c82d1e85b91a3655b093767ed
