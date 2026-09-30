# [C] Chamilo Authenticated Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-34239
Aliases: GHSA-4hwq-pv7c-3928
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-34239
Type: osv

## Details
Chamilo version 1.11.40 and earlier are vulnerable to authenticated remote code execution in the main/inc/ajax/lang.ajax.php path. This endpoint is protected only by `api_protect_course_script(true)`, which means any authenticated user enrolled in a course (student, teacher, DRH) can reach it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34239.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-4hwq-pv7c-3928
- https://nvd.nist.gov/vuln/detail/CVE-2026-34239
