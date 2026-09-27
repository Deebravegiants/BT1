# [C] CVE-2025-9152

## Summary
Severity: Critical
Advisory: CVE-2025-9152
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-9152
Type: osv

## Details
An improper privilege management vulnerability exists in WSO2 API Manager due to missing authentication and authorization checks in the keymanager-operations Dynamic Client Registration (DCR) endpoint.

A malicious user can exploit this flaw to generate access tokens with elevated privileges, potentially leading to administrative access and the ability to perform unauthorized operations.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-4483/
