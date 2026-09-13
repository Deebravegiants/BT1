# [M] MarkUs has a submission-view IDOR exposes all student submissions

## Summary
Severity: Medium
Advisory: CVE-2026-24900
Aliases: GHSA-56gh-8hmq-7q88
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24900
Type: osv

## Details
MarkUs is a web application for the submission and grading of student assignments. Prior to 2.9.1, the courses/<:course_id>/assignments/<:assignment_id>/submissions/html_content accepted a select_file_id parameter to serve SubmissionFile objects containing a record of files submitted by students. This parameter was not correctly scoped to the requesting user, allowing users access arbitrary submission file contents by id. This vulnerability is fixed in 2.9.1.

## References
- https://github.com/MarkUsProject/Markus/releases/tag/v2.9.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24900.json
- https://github.com/MarkUsProject/Markus/security/advisories/GHSA-56gh-8hmq-7q88
- https://nvd.nist.gov/vuln/detail/CVE-2026-24900
- https://github.com/MarkUsProject/Markus/commit/7daed9fd2d44932223798d997b55094a3bff104b
