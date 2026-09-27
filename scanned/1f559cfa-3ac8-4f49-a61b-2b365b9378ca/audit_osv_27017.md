# [M] CVE-2024-0392

## Summary
Severity: Medium
Advisory: CVE-2024-0392
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-0392
Type: osv

## Details
A Cross-Site Request Forgery (CSRF) vulnerability exists in the management console of WSO2 Enterprise Integrator 6.6.0 due to the absence of CSRF token validation. This flaw allows attackers to craft malicious requests that can trigger state-changing operations on behalf of an authenticated user, potentially compromising account settings and data integrity. The vulnerability only affects a limited set of state-changing operations, and successful exploitation requires social engineering to trick a user with access to the management console into performing the malicious action.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2024/WSO2-2023-2987/
