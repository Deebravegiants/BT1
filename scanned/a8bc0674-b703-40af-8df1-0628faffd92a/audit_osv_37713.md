# [H] Chamilo LMS has an IDOR in Gradebook Allows Cross-Course Evaluation Edit Without Ownership Check

## Summary
Severity: High
Advisory: CVE-2026-32930
Aliases: GHSA-9h22-wrg7-82q6
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-32930
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38 and 2.0.0-RC.3, an Insecure Direct Object Reference (IDOR) vulnerability in the gradebook evaluation edit page allows any authenticated teacher to view and modify the settings (name, max score, weight) of evaluations belonging to any other course by manipulating the editeval GET parameter. This vulnerability is fixed in 1.11.38 and 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32930.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-9h22-wrg7-82q6
- https://nvd.nist.gov/vuln/detail/CVE-2026-32930
- https://github.com/chamilo/chamilo-lms/commit/63e1e6d3d717bd537c7c61719416da35aaa658dd
- https://github.com/chamilo/chamilo-lms/commit/f03f681df939db0429edc8414fb3ce4e4b80d79d
