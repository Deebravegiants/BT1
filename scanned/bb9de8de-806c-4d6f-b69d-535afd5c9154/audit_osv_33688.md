# [H] Horilla Unauthorized Access to Candidate Resume Files Due to Broken Access Control

## Summary
Severity: High
Advisory: CVE-2025-48869
Aliases: GHSA-99h5-x29f-727w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-48869
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). Unauthenticated users can access uploaded resume files in Horilla 1.3.0 by directly guessing or predicting file URLs. These files are stored in a publicly accessible directory, allowing attackers to retrieve sensitive candidate information without authentication. At time of publication there is no known patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48869.json
- https://github.com/horilla-opensource/horilla/security/advisories/GHSA-99h5-x29f-727w
- https://nvd.nist.gov/vuln/detail/CVE-2025-48869
