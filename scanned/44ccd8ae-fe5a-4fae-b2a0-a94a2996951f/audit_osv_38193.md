# [H] Chamilo LMS has OS Command Injection via export_all_certificates action

## Summary
Severity: High
Advisory: CVE-2026-35196
Aliases: GHSA-crc6-r6c7-44q3
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-35196
Type: osv

## Details
Chamilo LMS is an open-source learning management system. In versions prior to 2.0.0-RC.3, an OS Command Injection vulnerability exists in the main/inc/ajax/gradebook.ajax.php endpoint within the export_all_certificates action, where the course code retrieved from the session variable $_SESSION['_cid'] via api_get_course_id() is concatenated directly into a shell_exec() command string without sanitization or escaping using escapeshellarg(). If an attacker can manipulate or poison their session data to inject shell metacharacters into the _cid variable, they can achieve arbitrary command execution on the underlying server. Successful exploitation grants full access to read system files and credentials, alters the application and database, or disrupts server availability. This issue has been fixed in version 2.0.0-RC.3.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v2.0.0-RC.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35196.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-crc6-r6c7-44q3
- https://nvd.nist.gov/vuln/detail/CVE-2026-35196
- https://github.com/chamilo/chamilo-lms/commit/62671e5e268f235cddfba704edee90f35c234df1
