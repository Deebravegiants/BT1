# [H] CVE-2025-10907

## Summary
Severity: High
Advisory: CVE-2025-10907
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-05
Source: https://osv.dev/vulnerability/CVE-2025-10907
Type: osv

## Details
An arbitrary file upload vulnerability exists in multiple WSO2 products due to insufficient validation of uploaded content and destination in SOAP admin services. A malicious actor with administrative privileges can upload a specially crafted file to a user-controlled location within the deployment.

Successful exploitation may lead to remote code execution (RCE) on the server, depending on how the uploaded file is processed. By default, this vulnerability is only exploitable by users with administrative access to the affected SOAP services.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-4603/
