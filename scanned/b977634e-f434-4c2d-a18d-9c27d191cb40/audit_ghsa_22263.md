# [M] Alkacon OpenCMS Absolute Path Traversal via pathname in filePath.0 parameter

## Summary
Severity: Medium
Advisory: GHSA-xxjj-jhgc-r68f
CVE: CVE-2008-1301
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-xxjj-jhgc-r68f
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=7.0.3 <7.0.5

## Details
Absolute path traversal vulnerability in system/workplace/admin/workplace/logfileview/logfileViewSettings.jsp in Alkacon OpenCms 7.0.3 and 7.0.4 allows remote authenticated administrators to read arbitrary files via a full pathname in the filePath.0 parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1301
- https://github.com/alkacon/opencms-core/commit/7b73b5559c1b025dfe0f7b38ed4119c25b9df409
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41096
- https://github.com/alkacon/opencms-core
- http://securityreason.com/securityalert/3731
