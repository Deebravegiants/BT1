# [H] Grav vulnerable to Privilege Escalation in Grav Admin: Missing Username Uniqueness Check Allows Admin Account Takeover

## Summary
Severity: High
Advisory: GHSA-cjcp-qxvg-4rjm
CVE: CVE-2025-66296
CWE: CWE-266
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-cjcp-qxvg-4rjm
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
### Summary
A privilege escalation vulnerability exists in Grav’s Admin plugin due to the absence of username uniqueness validation when creating users.
A user with the create user permission can create a new account using the same username as an existing administrator account, set a new password/email, and then log in as that administrator. This effectively allows privilege escalation from limited user-manager permissions to full administrator access.


### Steps to Reproduce
1. Make sure you have two accounts: an admin and a user with create user privilege
2. In the user account, navigate to /grav-admin/admin/accounts/users and click "Add"
3. Enter the name of the admin, complete registration and observe that the existing admin’s email is changed to the value you provided.
4. Log out from user account log in as admin with new credentials


### Impact
1. Full admin takeover by any user with create user permission.
2. Ability to change admin credentials, install/remove plugins, read or modify site data, and execute any action available to an admin.
3. Severity: High/Critical.


### PoC
https://github.com/user-attachments/assets/3ab0a7d6-5055-41be-9e0e-2bd6ca359b37

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-cjcp-qxvg-4rjm
- https://nvd.nist.gov/vuln/detail/CVE-2025-66296
- https://github.com/getgrav/grav/commit/3462d94d575064601689b236508c316242e15741
- https://github.com/getgrav/grav
