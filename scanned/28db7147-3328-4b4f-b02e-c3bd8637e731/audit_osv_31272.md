# [M] CVE-2024-7097

## Summary
Severity: Medium
Advisory: CVE-2024-7097
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-05-30
Source: https://osv.dev/vulnerability/CVE-2024-7097
Type: osv

## Details
An incorrect authorization vulnerability exists in multiple WSO2 products due to a flaw in the SOAP admin service, which allows user account creation regardless of the self-registration configuration settings. This vulnerability enables malicious actors to create new user accounts without proper authorization.

Exploitation of this flaw could allow an attacker to create multiple low-privileged user accounts, gaining unauthorized access to the system. Additionally, continuous exploitation could lead to system resource exhaustion through mass user creation.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2024/WSO2-2024-3574/
