# [M] OpenEMR's Message Update Ignores Patient id

## Summary
Severity: Medium
Advisory: CVE-2026-25745
Aliases: GHSA-jm78-x5p7-52qh
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-25745
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. In versions up to and including 8.0.0, the message/note update endpoint (e.g. PUT or POST) updates by message/note ID only and does not verify that the message belongs to the current patient (or that the user is allowed to edit that patient’s notes). An authenticated user with notes permission can modify any patient’s messages by supplying another message ID. Commit 92a2ff9eaaa80674b3a934a6556e35e7aded5a41 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25745.json
- https://github.com/openemr/openemr/security/advisories/GHSA-jm78-x5p7-52qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-25745
- https://github.com/openemr/openemr/commit/92a2ff9eaaa80674b3a934a6556e35e7aded5a41
