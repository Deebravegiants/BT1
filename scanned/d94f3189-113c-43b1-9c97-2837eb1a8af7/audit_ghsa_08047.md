# [C] carbon-apimgt does not properly restrict uploaded files

## Summary
Severity: Critical
Advisory: GHSA-p6jf-79j3-33f3
CVE: CVE-2025-13590
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-p6jf-79j3-33f3
Type: github-advisory

## Affected
- Maven: `org.wso2.carbon.apimgt:org.wso2.carbon.apimgt.rest.api.admin.v1` — affected >=0 <9.32.167

## Details
A malicious actor with administrative privileges can upload an arbitrary file to a user-controlled location within the deployment via a system REST API. Successful uploads may lead to remote code execution. 

 By leveraging the vulnerability, a malicious actor may perform Remote Code Execution by uploading a specially crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13590
- https://github.com/wso2/carbon-apimgt/pull/13560
- https://github.com/wso2/carbon-apimgt/commit/49a6427b39a5d9552ce97430858bb4b1912a3044
- https://github.com/wso2/carbon-apimgt
- https://github.com/wso2/carbon-apimgt/releases/tag/v9.32.167
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2026/WSO2-2025-4849
