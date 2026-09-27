# [H] CVE-2025-5717

## Summary
Severity: High
Advisory: CVE-2025-5717
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-5717
Type: osv

## Details
An authenticated remote code execution (RCE) vulnerability exists in multiple WSO2 products due to improper input validation in the event processor admin service. A user with administrative access to the SOAP admin services can exploit this flaw by deploying a Siddhi execution plan containing malicious Java code, resulting in arbitrary code execution on the server.

Exploitation of this vulnerability requires a valid user account with administrative privileges, limiting the attack surface to authenticated but potentially malicious users.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-4119/
