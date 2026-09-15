# [M] Object-Level Access Control Vulnerability Allows Unauthorized Access to Student Grades in Unifiedtransform

## Summary
Severity: Medium
Advisory: CVE-2024-12305
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/CVE-2024-12305
Type: osv

## Details
An object-level access control vulnerability in Unifiedtransform version 2.0 and potentially earlier versions allows unauthorized access to student grades. A malicious student user can view grades of other students by manipulating the student_id parameter in the marks viewing endpoint. The vulnerability exists due to insufficient access control checks in MarkController.php. At the time of publication of the CVE no patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12305.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12305
- https://github.com/changeweb/Unifiedtransform
- https://huntr.com/bounties/90a7299e-9233-43fd-b666-7375c4fdbb3c
