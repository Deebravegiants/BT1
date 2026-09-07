# [H] phpMyFAQ has an incomplete fix for GHSA-xvp4-phqj-cjr3 — editUser() and updateUserRights() lack authorization guards

## Summary
Severity: High
Advisory: GHSA-985r-q3qp-299h
CWE: CWE-832
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-985r-q3qp-299h
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.4
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.4

## Details
## Advisory / Disclosure

# phpMyFAQ 4.1.3 — incomplete fix for the admin-API IDOR/privilege-escalation class

**Target:** thorsten/phpMyFAQ (composer: `thorsten/phpmyfaq`, `phpmyfaq/phpmyfaq`)
**Affected:** <= 4.1.3 (the 4.1.3 security fix is incomplete; siblings remain)
**Class:** CWE-862 Missing Authorization / CWE-269 Improper Privilege Management / CWE-639 Authorization Bypass Through User-Controlled Key
**Methodology:** M1 incomplete-fix audit (sibling-walk of the 4.1.3 fix for GHSA-xvp4-phqj-cjr3)
**Severity:** High — CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H = 8.8 (same class as the parent CVE)

## Summary

phpMyFAQ 4.1.3 fixed **GHSA-xvp4-phqj-cjr3** ("IDOR Account Takeover") by adding actor-authorization guards to `UserController::overwritePassword()`. The patch establishes a new invariant, stated in its own code comments:

> "Only SuperAdmins may change other users' [attributes]. Self-service is
> always allowed." and "a non-SuperAdmin must never be able to alter a
> SuperAdmin or protected account."

That invariant is **not enforced** on two sibling endpoints in the *same file*, which the 4.1.3 fix left **unchanged**, and which carry the identical "user-controlled `userId` → `getUserById()` → privileged mutation" primitive — but with a strictly more dangerous sink:

| Endpoint | Route | Sink | Guard in 4.1.3 |
|----------|-------|------|----------------|
| `overwritePassword()` | `admin/api/user/overwrite-password` | `changePassword()` | **isSelf + isSuperAdmin + target-protection** (patched) |
| `editUser()` | `admin/api/user/edit` | `setSuperAdmin((bool)$req.is_superadmin)` | **none** (only `userHasPermission(USER_EDIT)`) |
| `updateUserRights()` | `admin/api/user/update-rights` | `grantUserRight($req.userId, …)` | **none** (only `userHasPermission(USER_EDIT)`) |

A logged-in administrator holding the delegable `edit_user` right — but  **not** SuperAdmin — can therefore:

1. Set their own (or anyone's) `is_superadmin` flag to `true` via `admin/api/user/edit` → **full privilege escalation to SuperAdmin**.
2. Grant arbitrary rights to any account via `admin/api/user/update-rights`.

This is exactly the threat model the parent advisory (GHSA-xvp4) calls out: "organizations with multiple admin users where not all should have SuperAdmin access."

## Anchors (upstream tag 4.1.3)

- `phpmyfaq/src/phpMyFAQ/Controller/Administration/Api/UserController.php`
  - `editUser()` lines 419-476; user-controlled `userId` at :433, user-controlled `is_superadmin` at :443, sink 
`$user >setSuperAdmin((bool)$isSuperAdmin)` at **:463**. Only gate: `userHasPermission(PermissionType::USER_EDIT)` at :422.
  - `updateUserRights()` lines 482-520; `userId` at :496, sink `grantUserRight($userId, …)` at **:511**. Only gate at :485.
  - `overwritePassword()` lines 419… → 228-288; the **patched** guards at: 254-260 and: 269-273.
- `phpmyfaq/src/phpMyFAQ/Controller/AbstractController.php` —`userHasPermission()` :221-227 (checks one right only; non SuperAdmins can hold it).
- `phpmyfaq/src/phpMyFAQ/User.php` — `setSuperAdmin()` :950-962 (`UPDATE faquser SET is_superadmin=… WHERE user_id=…`, no guard); `isSuperAdmin()` :942-945.
- `phpmyfaq/src/phpMyFAQ/Permission/BasicPermission.php` — `hasPermission()` :95-112 (SuperAdmin short-circuits true, else  `checkUserRight`).

Evidence snapshots in this folder:
`advisory/fix-diff-4.1.2-to-4.1.3.txt` (proves the fix touched only `overwritePassword`/`deleteUser`) and `advisory/vulnerable-siblings-4.1.3.txt` (the two unguarded methods as shipped). `git diff 4.1.2 4.1.3` shows **no change** to `editUser`, `updateUserRights`, `setSuperAdmin`, or `grantUserRight`.

## Proof of Concept

`poc/poc.php` (run log: `poc/run-log.txt`). Dependency-free: it builds phpMyFAQ's **real schema** (copied verbatim from
`src/phpMyFAQ/Instance/Database/Sqlite3.php`) and executes the **verbatim SQL** that the shipped 4.1.3 methods run —`setSuperAdmin` (UPDATE), `grantUserRight` (INSERT), and the real `hasPermission` / `checkUserRight` / `getRightId` queries — to prove the primitive:

- Seeds a SuperAdmin (`admin`, id=1) and a non-SuperAdmin admin (`editor`, id=2) granted only `add_user`/`edit_user`/`delete_user`.
- **Control:** the patched `overwritePassword` guard blocks `editor` changing the SuperAdmin (id=1) — confirms the fix works *there*.
- **Exploit 1:** `editor` (non-SuperAdmin, passes `userHasPermission(edit_user)`) flips their own `is_superadmin` 0→1 → SuperAdmin. `VULNERABLE`.
- **Exploit 2:** `editor` grants the `editconfig` right via `updateUserRights`. `VULNERABLE`.

Run:
```sh
php poc/poc.php   # -> RESULT: VULNERABLE ... EXIT 0
```

### PoC scope (honest)

The PoC exercises the **privilege-escalation primitive** (the unguarded sinks + the real authorization-resolution logic) against the real schema. The full HTTP exploit additionally requires an authenticated admin session and a CSRF token (`editUser` verifies `update-user-data`, `updateUserRights` verifies `update-user-rights`); both are available to the authenticated admin attacker — the parent advisory's own PoC shows reading the CSRF token from admin pages. The controller-level **absence of an authorization guard** is established by source citation (the only gate is `userHasPermission(USER_EDIT)`), corroborated by the fix diff showing these methods were not modified.

## Recommended fix

Apply the `overwritePassword` invariant to the siblings:
- `editUser()`: reject `is_superadmin`/status/2FA changes unless `$this->currentUser->isSuperAdmin()`; never allow a non-SuperAdmin to edit a SuperAdmin or `protected` target. Treat `is_superadmin` as a SuperAdmin-only field (defeat the mass-assignment at :443/:463).
- `updateUserRights()`: require `isSuperAdmin()` (or a privilege-level comparison) before `grantUserRight`; forbid granting rights the actor does not itself hold, and forbid targeting SuperAdmin/protected users.
- `activate()` (`admin/api/user/activate`, :194-221) is a lower-impact sibling with the same shape — apply the same guard.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-985r-q3qp-299h
- https://github.com/thorsten/phpMyFAQ
