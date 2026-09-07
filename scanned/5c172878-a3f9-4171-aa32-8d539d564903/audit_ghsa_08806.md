# [H] Grav Vulnerable to Administrative Account Disruption and Privilege De-escalation via User Overwrite Logic

## Summary
Severity: High
Advisory: GHSA-rr73-568v-28f8
CVE: CVE-2026-42609
CWE: CWE-269, CWE-285, CWE-639, CWE-837
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-rr73-568v-28f8
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
### Summary
A business logic vulnerability in the Grav Admin Panel allows a low-privileged user (with only user creation permissions) to overwrite existing accounts, including the primary administrator. By creating a new user with a username that already exists, the system updates the existing account's metadata and permissions instead of rejecting the request. This leads to a Denial of Service (DoS) on administrative functions and Privilege De-escalation of the root account.

### Details
The vulnerability stems from an insecure "Create or Update" logic within the user management module. When the admin-addon handles a user creation request, it does not strictly validate whether the username is already taken by a higher-privileged account. Instead of returning a "409 Conflict" or a validation error, the application logic proceeds to overwrite the existing user configuration file (e.g., user/accounts/root0.yaml) with the new, lower-privileged data provided by the attacker.
Because the attacker cannot assign higher permissions to themselves (due to existing fixes), the result is that the targeted account (the original Admin/Root) has its access levels wiped or replaced by the attacker's input, effectively locking the real administrator out of the system.

### PoC
1. Log in as a Super User (e.g., root0) and create a low-privileged user (e.g., adminuser).
2. Assign adminuser the following specific permissions:
admin.login
admin.users.list
admin.users.read
admin.users.create
3. Log out and log back in as adminuser.
4. Navigate to User Accounts -> Add.
5. Fill in the form with the following details:
Username: root0 (The exact username of the Super User)
Email: `anything@grav.f`
Fullname: Fake Root0
7. Click Save.
8. Observe that the account is successfully "created".
9. The original administrative permissions are gone, and the account is now restricted.

#### PoC video
https://github.com/user-attachments/assets/047cb44e-0279-402b-b4fb-12bf5d427a5e

### Impact
This is a Privilege De-escalation and Account Disruption vulnerability.
Who is impacted: Any Grav installation where a non-admin user is granted permission to create other users.
Consequence: An attacker can effectively disable all administrative accounts on the platform, leading to a complete loss of management control over the CMS.


---

## Maintainer note — fix applied (2026-04-24)

Fixed in Grav core on the `2.0` branch: commit [`d904efc33`](https://github.com/getgrav/grav/commit/d904efc33) — will ship in **2.0.0-beta.2**.

**What changed:** `UserObject::save` already had a uniqueness guard (commit [`19c2f8da7`](https://github.com/getgrav/grav/commit/19c2f8da7), November 2025) that blocks the PoC. This release tightens that guard:

1. `strpos($key, '@@')` → `str_contains($key, '@@')`. The previous form was falsy when the transient-key marker was at position 0 (e.g. `@@hash`), silently bypassing the check. `str_contains` returns a proper boolean.
2. The `instanceof FileStorage` gate was dropped so the uniqueness check runs for any `FlexStorageInterface` backend — not just the default file-per-user YAML one.

A low-privileged user with `admin.users.create` can no longer disrupt a super-admin account by submitting that admin's username through the "add user" form.

**Files:**
- [`system/src/Grav/Common/Flex/Types/Users/UserObject.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Flex/Types/Users/UserObject.php).
- [`tests/unit/Grav/Common/Security/UserOverwriteSecurityTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/UserOverwriteSecurityTest.php) — 3 tests pinning the PoC, the `@@`-prefix edge case, and pass-through for free usernames.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-rr73-568v-28f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-42609
- https://github.com/getgrav/grav/commit/5a12f9be8314682c8713e569e330f11805d0a663
- https://github.com/getgrav/grav/commit/c66dfeb5ff679a1667678c6335eb9ff3255dfc47
- https://github.com/getgrav/grav/commit/d904efc33e03ebb597afde8d3368b28cf0423632
- https://github.com/getgrav/grav
