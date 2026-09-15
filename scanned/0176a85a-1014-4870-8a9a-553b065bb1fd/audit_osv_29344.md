# [H] Apache CloudStack: User Key Exposure to Domain Admins

## Summary
Severity: High
Advisory: CVE-2024-42062
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-42062
Type: osv

## Details
CloudStack account-users by default use username and password based authentication for API and UI access. Account-users can generate and register randomised API and secret keys and use them for the purpose of API-based automation and integrations. Due to an access permission validation issue that affects Apache CloudStack versions 4.10.0 up to 4.19.1.0, domain admin accounts were found to be able to query all registered account-users API and secret keys in an environment, including that of a root admin. An attacker who has domain admin access can exploit this to gain root admin and other-account privileges and perform malicious operations that can result in compromise of resources integrity and confidentiality, data loss, denial of service and availability of CloudStack managed infrastructure.

Users are recommended to upgrade to Apache CloudStack 4.18.2.3 or 4.19.1.1, or later, which addresses this issue. Additionally, all account-user API and secret keys should be regenerated.

## References
- http://www.openwall.com/lists/oss-security/2024/08/06/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42062.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42062
- https://www.shapeblue.com/shapeblue-security-advisory-apache-cloudstack-security-releases-4-18-2-3-and-4-19-1-1/
- https://cloudstack.apache.org/blog/security-release-advisory-4.19.1.1-4.18.2.3
- https://lists.apache.org/thread/lxqtfd6407prbw3801hb4fz3ot3t8wlj
