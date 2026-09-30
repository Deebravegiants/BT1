# [M] CVE-2025-9804

## Summary
Severity: Medium
Advisory: CVE-2025-9804
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-9804
Type: osv

## Details
An improper access control vulnerability exists in multiple WSO2 products due to insufficient permission enforcement in certain internal SOAP Admin Services and System REST APIs. A low-privileged user may exploit this flaw to perform unauthorized operations, including accessing server-level information.

This vulnerability affects only internal administrative interfaces. APIs exposed through the WSO2 API Manager's API Gateway remain unaffected.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-4503/
