# [H] phpMyFAQ privilege escalation: GroupController::updatePermissions lets a GROUP_EDIT admin grant rights they do not hold

## Summary
Severity: High
Advisory: GHSA-pg62-f8g4-4wqh
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-pg62-f8g4-4wqh
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.5
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.5

## Details
## Overview

When phpMyFAQ hardened its admin permission-assignment endpoints against privilege escalation, it added a "a non-SuperAdmin may only assign rights they themselves hold" constraint to the user-rights endpoint (`UserController::updateUserRights`). **The equivalent group-rights endpoint, `GroupController::updatePermissions`, did not receive that constraint.** A delegated administrator holding only the `GROUP_EDIT` permission can therefore grant any group an arbitrary set of rights — including rights the administrator does not possess — and, by being (or becoming) a member of that group, inherit those rights, escalating to higher privileges up to full administrative control.

## Impact

phpMyFAQ supports delegated administration: the `GROUP_EDIT` right can be granted to a non-SuperAdmin so they can manage groups. Such an administrator can escalate:

1. They call `POST /admin/group/update/permissions` with `group_id` set to a group they belong to (or can manage membership of) and `group_rights[]` containing high-value rights they do **not** themselves hold (e.g. user administration, or any right gating sensitive actions).
2. The endpoint grants every requested right to the group with no check that the caller holds them.
3. Members of that group — including the attacker — inherit the granted rights, escalating the attacker's effective privileges.

This is the group-side mirror of exactly what the maintainers blocked on the user-rights side, where the code comment names the threat explicitly ("prevents an administrator with the delegable USER_EDIT right from granting privileges they do not possess (privilege escalation)"). The group path remains open.

`PR:L` (the attacker needs the delegable `GROUP_EDIT` right, below SuperAdmin), `S:U` (escalation within phpMyFAQ's single authorization authority), `C:H/I:H/A:H` (inherited rights can reach full administrative read/write/availability control). The one added step versus the user-rights path — the attacker must be a member of the group they elevate (a GROUP_EDIT admin generally manages group membership, hence `AC:L`) — is noted in Technical Details.

## Technical Details

References are to `phpmyfaq/src/phpMyFAQ/` at HEAD `04db2b999d8d`.

**The vulnerable endpoint — no self-rights check (`Controller/Administration/GroupController.php:309-349`):**

```php
#[Route(path: '/group/update/permissions', name: 'admin.group.update.permissions', methods: ['POST'])]
public function updatePermissions(Request $request): Response
{
    $this->userHasPermission(PermissionType::GROUP_EDIT);     // only requires GROUP_EDIT — not SuperAdmin, no per-right check
    // ... CSRF verified ...
    $groupId = (int) Filter::filterVar($request->request->get('group_id'), FILTER_VALIDATE_INT);
    $groupPermissions = $request->request->all()['group_rights'];   // attacker-controlled list of right IDs

    $refuseResult = $this->user->perm->refuseAllGroupRights($groupId);
    if ($refuseResult) {
        foreach ($groupPermissions as $groupPermission) {
            $this->user->perm->grantGroupRight($groupId, (int) $groupPermission);   // grants ANY right, unconstrained
        }
        ...
    }
}
```

Each `group_rights[]` entry is granted to the group verbatim; there is no verification that the acting administrator holds that right.

**The fixed sibling — `updateUserRights` DOES constrain to self-held rights (`Controller/Administration/Api/UserController.php:558-579`):**

```php
$actingIsSuperAdmin = $this->currentUser->isSuperAdmin();
// A non-SuperAdmin may only assign rights they hold themselves. This prevents an
// administrator with the delegable USER_EDIT right from granting privileges they do not
// possess (privilege escalation).
if (!$actingIsSuperAdmin) {
    $actingUserId = $this->currentUser->getUserId();
    foreach ($userRights as $userRight) {
        if (!$this->currentUser->perm->hasPermission($actingUserId, (int) $userRight)) {
            return $this->json(['error' => Translation::get(key: 'msgNoPermission')], Response::HTTP_FORBIDDEN);
        }
    }
}
```

The identical "may only assign rights you hold" loop is present for user rights but **absent** for group rights. The group endpoint's only gate is `userHasPermission(GROUP_EDIT)` (`Controller/AbstractController.php`/`AbstractAdministrationController.php`), which checks the caller holds `GROUP_EDIT` — not that they hold each right being granted. This is an authorization **omission**: the enforcer the maintainers already wrote for the analogous mass-assignment of rights is simply not applied on the group path.

**Inheritance step (honest precondition).** `grantGroupRight` grants the right to the *group*; the attacker realizes the escalation by being a member of the elevated group. A `GROUP_EDIT` administrator manages groups (and typically their membership), so they can target a group they already belong to or add themselves — keeping `AC:L`. If a given deployment separates group-membership management from `GROUP_EDIT`, the attacker is limited to elevating groups they already belong to, which is still the common case for a delegated group admin.

## Reproduction

phpMyFAQ is self-hosted; reproduce on your own test instance. Create a non-SuperAdmin account granted `GROUP_EDIT` (and member of some group `G`), log in as it, and run in the DevTools Console:

```js
// Run as the delegated (non-SuperAdmin) GROUP_EDIT admin, on the phpMyFAQ admin UI.
// Grant group G (a group the attacker belongs to) a right the attacker does NOT hold
// (use a numeric RIGHT_ID for a high-value permission the account lacks, e.g. user admin).
const csrf = document.querySelector('[name="pmf-csrf-token"], #pmf-csrf-token')?.value
  || window.PMF_CSRF_UPDATE_GROUP_PERMISSIONS;  // the update-group-permissions token rendered on the group page
const body = new URLSearchParams();
body.set("pmf-csrf-token", csrf);
body.set("group_id", String(/* G's group id */ 2));
body.append("group_rights[]", String(/* RIGHT_ID the attacker lacks */ 1));
fetch("/admin/group/update/permissions", { method: "POST", credentials: "include", body })
  .then((r) => r.text())
  .then((t) => console.log(t.includes("savedsuc") ? "GRANTED (200)" : t.slice(0, 200)));
```

Expected result: the response reports success (`ad_msg_savedsuc_*`), i.e. the right was granted to group G even though the acting admin does not hold it. Confirm with `SELECT * FROM faqgroup_right WHERE group_id=2` (or the app's group-rights view) that the new `right_id` is present, then verify the attacker (a member of G) now exercises the inherited right. (Against `updateUserRights` the same attempt to assign an unheld right returns `403 msgNoPermission`, demonstrating the missing constraint is specific to the group path.)

### End-to-end (source) verification

Authorization-omission finding; the gap is open at HEAD and reaches the privilege-grant sink with no intervening per-right check:

- **Endpoint reachable by a delegated non-SuperAdmin:** `updatePermissions` gate is `userHasPermission(PermissionType::GROUP_EDIT)` (`:311`) — confirmed it does not require SuperAdmin nor check the granted rights.
- **Attacker controls the granted rights:** `group_rights[]` from the request body, granted in the loop at `:329`.
- **Missing control:** the self-rights loop present in `updateUserRights` (`UserController.php:563-571`) has no counterpart in `updatePermissions` — verified by reading both handlers at HEAD.
- **Sink:** `MediumPermission::grantGroupRight` -> `INSERT INTO faqgroup_right` (Permission repository), persisting the unheld right to the group; members of the group inherit it.

## Suggested Fix

Apply the same self-rights constraint `updateUserRights` already has, before granting:

```php
$actingIsSuperAdmin = $this->currentUser->isSuperAdmin();
if (!$actingIsSuperAdmin) {
    $actingUserId = $this->currentUser->getUserId();
    foreach ($groupPermissions as $groupPermission) {
        if (!$this->currentUser->perm->hasPermission($actingUserId, (int) $groupPermission)) {
            throw new UnauthorizedHttpException('Cannot grant a right you do not hold');
        }
    }
}
```

More robustly, factor the "you may only assign rights you hold" rule into the permission layer (`grantGroupRight` / `grantUserRight`) so both the user-rights and group-rights paths enforce it uniformly, and add a regression test mirroring `testUpdateRightsNonSuperAdminCannotGrantRightTheyDoNotHold` for the group endpoint. (See also the related sibling gaps in the same admin-API authorization series: `UserController::addUser` missing the acting-SuperAdmin guard, and the `user/data` / `user/permissions` target-authorization on read.)

## Disclosure Timeline

- 2026-05-30: Discovered while auditing the completeness of the GHSA-xvp4 / GHSA-985r / GHSA-8c6h admin-API authorization-hardening series at `main` HEAD `04db2b999d8d`. The self-rights constraint added to `updateUserRights` was confirmed absent on the `GroupController::updatePermissions` sibling by reading both handlers + the permission gate + the `grantGroupRight` sink.
- 2026-05-30: Drafted for submission via GitHub Security Advisory.

## References

- Hardening series this incompletely fixes: GHSA-xvp4-phqj-cjr3, GHSA-985r-q3qp-299h ("incomplete fix for GHSA-xvp4"), GHSA-8c6h-7g6x-m5x4 ("incomplete fix for CVE-2026-24421").
- Affected source: `phpmyfaq/src/phpMyFAQ/Controller/Administration/GroupController.php:309-349` (`updatePermissions`, gate `userHasPermission(GROUP_EDIT)` at `:311`, sink `grantGroupRight` at `:329`); fixed sibling `Controller/Administration/Api/UserController.php:534-589` (`updateUserRights`, self-rights loop at `:563-566`); `Controller/AbstractController.php:326-336` (`userHasPermission`, the only gate — `GROUP_EDIT` action permission).
- Companion advisory (same audit, same series): `user/add` missing acting-SuperAdmin guard -> delegated admin creates SuperAdmin (8.8 High).

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-pg62-f8g4-4wqh
- https://github.com/thorsten/phpMyFAQ/commit/de5016607dd606ef161cccd10fa5deec303c834e
- https://github.com/thorsten/phpMyFAQ
