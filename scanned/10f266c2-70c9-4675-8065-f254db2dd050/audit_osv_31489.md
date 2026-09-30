# [H] CVE-2025-12737

## Summary
Severity: High
Advisory: CVE-2025-12737
CVSS: 8.4 (CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2025-12737
Type: osv

## Details
The administrative operations within the Carbon Console do not adequately validate specific user-supplied input. This oversight allows a malicious actor with administrative privileges to inject and execute arbitrary code remotely.

Successful exploitation enables a threat actor with administrative privileges and Carbon Console access to execute remote arbitrary code through specific administrative operations, leading to a complete compromise of the affected system.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2026/WSO2-2025-4771/
