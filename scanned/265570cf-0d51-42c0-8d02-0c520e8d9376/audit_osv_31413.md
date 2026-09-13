# [C] CVE-2025-10611

## Summary
Severity: Critical
Advisory: CVE-2025-10611
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-10611
Type: osv

## Details
Due to an insufficient access control implementation in multiple WSO2 Products, authentication and authorization checks for certain REST APIs can be bypassed, allowing them to be invoked without proper validation.

Successful exploitation of this vulnerability could lead to a malicious actor gaining administrative access and performing unauthenticated and unauthorized administrative operations.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-4585/
