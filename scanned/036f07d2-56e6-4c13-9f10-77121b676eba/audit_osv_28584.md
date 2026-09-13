# [M] CVE-2024-3511

## Summary
Severity: Medium
Advisory: CVE-2024-3511
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-06-23
Source: https://osv.dev/vulnerability/CVE-2024-3511
Type: osv

## Details
An incorrect authorization vulnerability exists in multiple WSO2 products that allows unauthorized access to versioned files stored in the registry. Due to flawed authorization logic, a malicious actor with access to the management console can exploit a specific bypass method to retrieve versioned files without proper authorization.

Successful exploitation of this vulnerability could lead to unauthorized disclosure of configuration or resource files that may be stored as registry versions, potentially aiding further attacks or system reconnaissance.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2024-2702/
