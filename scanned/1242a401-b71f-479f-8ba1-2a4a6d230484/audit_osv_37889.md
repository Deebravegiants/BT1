# [M] Chamilo LMS has unauthenticated access to Twig template source files exposes application logic

## Summary
Severity: Medium
Advisory: CVE-2026-33705
Aliases: GHSA-5wjg-8x28-px57
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33705
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38, Twig template files (.tpl) under /main/template/default/ are directly accessible without authentication via HTTP GET requests. These templates expose internal application logic, variable names, AJAX endpoint URLs, and admin panel structure. This vulnerability is fixed in 1.11.38.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33705.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-5wjg-8x28-px57
- https://nvd.nist.gov/vuln/detail/CVE-2026-33705
- https://github.com/chamilo/chamilo-lms/commit/4efb5ee8ed849ca147ca1fe7472ef7b98db17bff
