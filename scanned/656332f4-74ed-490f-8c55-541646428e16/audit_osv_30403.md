# [C] common-user-management Unrestricted File Upload Leading to Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2024-52302
Aliases: GHSA-rhcq-44g3-5xcx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-52302
Type: osv

## Details
common-user-management is a robust Spring Boot application featuring user management services designed to control user access dynamically. There is a critical security vulnerability in the application endpoint /api/v1/customer/profile-picture. This endpoint allows file uploads without proper validation or restrictions, enabling attackers to upload malicious files that can lead to Remote Code Execution (RCE).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52302.json
- https://github.com/OsamaTaher/Java-springboot-codebase/security/advisories/GHSA-rhcq-44g3-5xcx
- https://nvd.nist.gov/vuln/detail/CVE-2024-52302
- https://github.com/OsamaTaher/Java-springboot-codebase/commit/204402bb8b68030c14911379ddc82cfff00b8538
