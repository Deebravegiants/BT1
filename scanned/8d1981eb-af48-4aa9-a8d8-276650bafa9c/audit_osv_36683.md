# [C] Zip Slip in MarkUs config upload allowing RCE

## Summary
Severity: Critical
Advisory: CVE-2026-25057
Aliases: GHSA-mccg-p332-252h
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25057
Type: osv

## Details
MarkUs is a web application for the submission and grading of student assignments. Prior to 2.9.1, instructors are able to upload a zip file to create an assignment from an exported configuration (courses/<:course_id>/assignments/upload_config_files). The uploaded zip file entry names are used to create paths to write files to disk without checking these paths. This vulnerability is fixed in 2.9.1.

## References
- https://github.com/MarkUsProject/Markus/releases/tag/v2.9.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25057.json
- https://github.com/MarkUsProject/Markus/security/advisories/GHSA-mccg-p332-252h
- https://nvd.nist.gov/vuln/detail/CVE-2026-25057
- https://github.com/MarkUsProject/Markus/commit/0ca002a1f0071c7a00dbb2ed34fede57323c5dc7
