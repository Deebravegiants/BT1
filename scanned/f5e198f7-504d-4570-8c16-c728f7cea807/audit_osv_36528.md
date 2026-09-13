# [M] Horilla has Improper Access Control Issue that Allows Unauthorized Document Upload on Behalf of Another Employee

## Summary
Severity: Medium
Advisory: CVE-2026-24035
Aliases: GHSA-fm3f-xpgx-8xr3
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-24035
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). An Improper Access Control vulnerability exists in Horilla HR Software starting in version 1.4.0 and prior to version 1.5.0, allowing any authenticated employee to upload documents on behalf of another employee without proper authorization. This occurs due to insufficient server-side validation of the employee_id parameter during file upload operations, allowing any authenticated employee to upload document in behalf of any employee. Version 1.5.0 fixes the issue.

## References
- https://drive.google.com/file/d/1i00-NnipvxH8bGY-SyqEjnDQfxIbVGRR/view?usp=sharing
- https://github.com/horilla-opensource/horilla/releases/tag/1.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24035.json
- https://github.com/horilla-opensource/horilla/security/advisories/GHSA-fm3f-xpgx-8xr3
- https://nvd.nist.gov/vuln/detail/CVE-2026-24035
