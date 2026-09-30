# [M] CVE-2025-5605

## Summary
Severity: Medium
Advisory: CVE-2025-5605
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-24
Source: https://osv.dev/vulnerability/CVE-2025-5605
Type: osv

## Details
An authentication bypass vulnerability exists in the Management Console of multiple WSO2 products. A malicious actor with access to the console can manipulate the request URI to bypass authentication and access certain restricted resources, resulting in partial information disclosure.

The known exposure from this issue is limited to memory statistics. While the vulnerability does not allow full account compromise, it still enables unauthorized access to internal system details.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-4115/
