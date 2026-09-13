# [H] Chamilo LMS has an Insecure Direct Object Reference (IDOR)

## Summary
Severity: High
Advisory: CVE-2026-33702
Aliases: GHSA-3rv7-9fhx-j654
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33702
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38 and 2.0.0-RC.3, Chamilo LMS contains an Insecure Direct Object Reference (IDOR) vulnerability in the Learning Path progress saving endpoint. The file lp_ajax_save_item.php accepts a uid (user ID) parameter directly from $_REQUEST and uses it to load and modify another user's Learning Path progress — including score, status, completion, and time — without verifying that the requesting user matches the target user ID. Any authenticated user enrolled in a course can overwrite another user's Learning Path progress by simply changing the uid parameter in the request. This vulnerability is fixed in 1.11.38 and 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33702.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-3rv7-9fhx-j654
- https://nvd.nist.gov/vuln/detail/CVE-2026-33702
- https://github.com/chamilo/chamilo-lms/commit/6331d051b4468deb5830c01d1e047c5e5cf2c74f
- https://github.com/chamilo/chamilo-lms/commit/bf3f6c6949b5c882b48a9914baa19910417e4551
