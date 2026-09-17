# [H] Chamilo: OS Command Injection in /main/admin/sub_language_ajax.inc.php via POST new_language parameter

## Summary
Severity: High
Advisory: CVE-2025-50197
Aliases: GHSA-m76m-95c9-6h7r
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2025-50197
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.30, there is an OS Command Injection vulnerability in /main/admin/sub_language_ajax.inc.php via the POST new_language parameter. This issue has been patched in version 1.11.30.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50197.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-m76m-95c9-6h7r
- https://nvd.nist.gov/vuln/detail/CVE-2025-50197
- https://github.com/chamilo/chamilo-lms/commit/e1c7879d63172cd7e5e47c9a03ade0e32023e134
