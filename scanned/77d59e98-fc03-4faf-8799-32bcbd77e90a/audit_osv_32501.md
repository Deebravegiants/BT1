# [H] CVE-2025-3125

## Summary
Severity: High
Advisory: CVE-2025-3125
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-05
Source: https://osv.dev/vulnerability/CVE-2025-3125
Type: osv

## Details
An arbitrary file upload vulnerability exists in multiple WSO2 products due to improper input validation in the CarbonAppUploader admin service endpoint. An authenticated attacker with appropriate privileges can upload a malicious file to a user-controlled location on the server, potentially leading to remote code execution (RCE).

This functionality is restricted by default to admin users; therefore, successful exploitation requires valid credentials with administrative permissions.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-3961/
