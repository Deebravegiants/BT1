# [M] MarkUs: Zip bomb in config upload enables DoS

## Summary
Severity: Medium
Advisory: CVE-2026-25962
Aliases: GHSA-x8xv-j7fc-65x5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-25962
Type: osv

## Details
MarkUs is a web application for the submission and grading of student assignments. Prior to version 2.9.4, MarkUs currently extracts zip files without any size or entry-count limits. For example, instructors can upload a zip file to provide an assignment configuration; students can upload a zip file for an assignment submission and indicate its contents should be extracted. This issue has been patched in version 2.9.4.

## References
- https://github.com/MarkUsProject/Markus/releases/tag/v2.9.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25962.json
- https://github.com/MarkUsProject/Markus/security/advisories/GHSA-x8xv-j7fc-65x5
- https://nvd.nist.gov/vuln/detail/CVE-2026-25962
