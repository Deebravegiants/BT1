# [H] CVE-2024-6832

## Summary
Severity: High
Advisory: CVE-2024-6832
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2024-6832
Type: osv

## Details
The account locking mechanism fails to trigger when secondary user stores are inaccessible. The software does not maintain a consistent state for account locking if it cannot reach all configured user stores, allowing an attacker to repeatedly attempt authentication with invalid credentials without triggering the lockout mechanism for users within active stores.

When the account locking mechanism is bypassed due to the inaccessibility of secondary user stores, users in accessible user stores are left vulnerable to brute force attacks. A malicious actor can exploit this by attempting numerous invalid password combinations against a user account without the expected account lockout consequence.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2026/WSO2-2024-3352/
