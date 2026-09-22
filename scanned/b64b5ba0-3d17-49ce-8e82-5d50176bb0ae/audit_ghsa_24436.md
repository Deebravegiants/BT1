# [M] Alkacon OpenCMS Improper Access Control via system/workplace/views/admin/admin-main.jsp

## Summary
Severity: Medium
Advisory: GHSA-v3c3-qr6m-8m7m
CVE: CVE-2006-3935
CWE: CWE-284, CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-v3c3-qr6m-8m7m
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=0 <6.2.2

## Details
system/workplace/views/admin/admin-main.jsp in Alkacon OpenCms before 6.2.2 does not restrict access to administrator functions, which allows remote authenticated users to (1) send broadcast messages to all users (/workplace/broadcast), (2) list all users (/accounts/users), (3) add webusers (/accounts/webusers/new), (4) upload database import and export files (/database/importhttp), (5) upload arbitrary program modules (/modules/modules_import), and (6) read the log file (/workplace/logfileview) by setting the appropriate value for the path parameter in a direct request to admin-main.jsp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-3935
- https://github.com/alkacon/opencms-core/commit/8f1c04c5a16fe8d0bdbd13b65bf2a7b5cf100ff9
- https://exchange.xforce.ibmcloud.com/vulnerabilities/27996
- https://exchange.xforce.ibmcloud.com/vulnerabilities/28003
- https://exchange.xforce.ibmcloud.com/vulnerabilities/28010
- https://exchange.xforce.ibmcloud.com/vulnerabilities/28026
- https://exchange.xforce.ibmcloud.com/vulnerabilities/28031
- https://exchange.xforce.ibmcloud.com/vulnerabilities/28036
- https://github.com/alkacon/opencms-core
- http://www.opencms.org/export/download/opencms/opencms_6.2.2_src.zip
