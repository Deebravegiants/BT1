# [M] Apache CloudStack: Lack of user permission validation leading to data leak for few APIs

## Summary
Severity: Medium
Advisory: CVE-2025-59454
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-11-27
Source: https://osv.dev/vulnerability/CVE-2025-59454
Type: osv

## Details
In Apache CloudStack, a gap in access control checks affected the APIs - createNetworkACL
- listNetworkACLs
- listResourceDetails
- listVirtualMachinesUsageHistory
- listVolumesUsageHistory

While these APIs were accessible only to authorized users, insufficient permission validation meant that users could occasionally access information beyond their intended scope.




Users are recommended to upgrade to Apache CloudStack 4.20.2.0 or 4.22.0.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/11/27/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59454.json
- https://lists.apache.org/thread/0hlklvlwhzsfw39nocmyxb6svjbs9xbc
- https://nvd.nist.gov/vuln/detail/CVE-2025-59454
