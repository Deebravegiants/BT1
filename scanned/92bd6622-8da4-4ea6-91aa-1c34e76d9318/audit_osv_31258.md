# [C] CVE-2024-6914

## Summary
Severity: Critical
Advisory: CVE-2024-6914
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2024-6914
Type: osv

## Details
An incorrect authorization vulnerability exists in multiple WSO2 products due to a business logic flaw in the account recovery-related SOAP admin service. A malicious actor can exploit this vulnerability to reset the password of any user account, leading to a complete account takeover, including accounts with elevated privileges.

This vulnerability is exploitable only through the account recovery SOAP admin services exposed via the "/services" context path in affected products. The impact may be reduced if access to these endpoints has been restricted based on the "Security Guidelines for Production Deployment" by disabling exposure to untrusted networks.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2024/WSO2-2024-3561/
- https://security.docs.wso2.com/en/latest/security-guidelines/security-guidelines-for-production-deployment/
