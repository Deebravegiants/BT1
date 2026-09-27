# [M] CVE-2025-66911

## Summary
Severity: Medium
Advisory: CVE-2025-66911
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2025-66911
Type: osv

## Details
Turms IM Server v0.10.0-SNAPSHOT and earlier contains a broken access control vulnerability in the user online status query functionality. The handleQueryUserOnlineStatusesRequest() method in UserServiceController.java allows any authenticated user to query the online status, device information, and login timestamps of arbitrary users without proper authorization checks.

## References
- https://github.com/Xzzz111/public_cve_report/blob/main/CVE-2025-66911_report.md
- https://github.com/turms-im/turms/blob/develop/turms-service/src/main/java/im/turms/service/domain/user/access/servicerequest/controller/UserServiceController.java#L239
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66911.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66911
- https://github.com/turms-im/turms
