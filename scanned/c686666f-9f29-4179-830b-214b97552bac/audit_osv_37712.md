# [H] Chamilo LMS has an IDOR in Gradebook Allows Cross-Course Deletion of Any Student's Grade Result

## Summary
Severity: High
Advisory: CVE-2026-32894
Aliases: GHSA-rqpg-p95v-fv98
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-32894
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38 and 2.0.0-RC.3, an Insecure Direct Object Reference (IDOR) vulnerability in the gradebook result view page allows any authenticated teacher to delete any student's grade result across the entire platform by manipulating the delete_mark or resultdelete GET parameters. No ownership or course-scope verification is performed. This vulnerability is fixed in 1.11.38 and 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32894.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-rqpg-p95v-fv98
- https://nvd.nist.gov/vuln/detail/CVE-2026-32894
- https://github.com/chamilo/chamilo-lms/commit/3b03306d1a0301a81b9284e86893b27f518ab151
- https://github.com/chamilo/chamilo-lms/commit/740f5a6e192a52a3adde3c3241c86401b1d2c519
