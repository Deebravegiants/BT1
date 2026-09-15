# [M] Horilla's Improper Access Control Allows Employees to Auto-Approve Documents

## Summary
Severity: Medium
Advisory: CVE-2026-24039
Aliases: GHSA-99mq-mhwv-w9qx
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-24039
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). Version 1.4.0 has Improper Access Control, allowing low-privileged employees to self-approve documents they have uploaded. The document-approval UI is intended to be restricted to administrator or high-privilege roles only; however, an insufficient server-side authorization check on the approval endpoint lets a standard employee modify the approval status of their own uploaded document. A successful exploitation allows users with only employee-level permissions to alter application state reserved for administrators. This undermines the integrity of HR processes (for example, acceptance of credentials, certifications, or supporting materials), and may enable submission of unvetted documents. This issue is fixed in version 1.5.0.

## References
- https://github.com/horilla-opensource/horilla/releases/tag/1.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24039.json
- https://github.com/horilla-opensource/horilla/security/advisories/GHSA-99mq-mhwv-w9qx
- https://nvd.nist.gov/vuln/detail/CVE-2026-24039
