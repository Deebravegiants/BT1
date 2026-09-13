# [M] Admidio Exposes Cross-Organization Member Data via Permission Check Mismatch in contacts_data.php

## Summary
Severity: Medium
Advisory: GHSA-g8p8-94f2-28gr
CVE: CVE-2026-41657
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-g8p8-94f2-28gr
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

The `contacts_data.php` endpoint uses a weaker permission check (`isAdministratorUsers()`, requiring only `rol_edit_user=true`) than the frontend UI (`contacts.php`) which correctly requires the stronger `isAdministrator()` (requiring `rol_administrator=true`) and the `contacts_show_all` system setting. A user manager who is not a full administrator can directly request `contacts_data.php?mem_show_filter=3` to retrieve all user records across all organizations in the Admidio instance, bypassing multi-tenant organization isolation.

## Details

The frontend page `contacts.php` and the backend data endpoint `contacts_data.php` have mismatched authorization checks for the "show all organizations" filter (`mem_show_filter=3`).

**Frontend guard** at `modules/contacts/contacts.php:80`:
```php
if ($gCurrentUser->isAdministrator() && $gSettingsManager->getBool('contacts_show_all')) {
    // Only then is filter=3 ("All Organizations") shown in the dropdown
    $selectBoxValues = array(
        ...
        '3' => array('3', $gL10n->get('SYS_ALL_CONTACTS'), $gL10n->get('SYS_ALL_ORGANIZATIONS'))
    );
}
```
This correctly requires both `isAdministrator()` (`rol_administrator=true`) AND the `contacts_show_all` setting.

**Backend check** at `modules/contacts/contacts_data.php:235`:
```php
} elseif (($getMembersShowFilter === 3) && $gCurrentUser->isAdministratorUsers()) {
    $mainSql = $contactsListConfig->getSql(
        array(
            'showAllMembersDatabase' => true,
            ...
        )
    );
```
This only requires `isAdministratorUsers()` which checks `rol_edit_user=true` — a weaker permission available to non-admin "user manager" roles. The `contacts_show_all` setting is never checked.

**The critical difference between the two methods** (from `src/Users/Entity/User.php`):
- `isAdministrator()` (line 1507): checks the `rol_administrator` flag — full system administrator
- `isAdministratorUsers()` (line 1625): checks `rol_edit_user` right — user management module access only

When `showAllMembersDatabase=true` reaches `ListConfiguration::getSql()` (at `src/Roles/Entity/ListConfiguration.php:1022-1028`), the generated SQL removes ALL organization filtering:
```php
} elseif ($optionsAll['showAllMembersDatabase']) {
    $sql = 'SELECT DISTINCT ' . $sqlMemLeader . $sqlIdColumns . $sqlColumnNames . '
              FROM ' . TBL_USERS . '
                   ' . $sqlJoin . '
             WHERE usr_valid = true ' .
        $sqlWhere .
        $sqlOrderBys;
}
```

Compare with the default query which includes `cat_org_id = $gCurrentOrgId` to restrict results to the current organization.

The cross-org indicator subqueries at line 169 do correctly check `isAdministrator()`, so the `member_other_orga` columns return 0 — but this only affects display indicators, not the actual user data returned.

## PoC

**Prerequisites:** An Admidio instance with at least two organizations sharing the same database. A user account in Organization A assigned to a role with `rol_edit_user=1` but `rol_administrator=0`.

**Step 1:** Log in as the user manager account and capture the session cookie.

**Step 2:** Request all users across all organizations by directly calling the data endpoint:
```bash
curl -s -b 'PHPSESSID=<user_manager_session>' \
  'https://target/adm_program/modules/contacts/contacts_data.php?mem_show_filter=3&draw=1&start=0&length=100&search%5Bvalue%5D='
```

**Expected behavior:** The request should be rejected or return only current-organization users, since the user is not a full administrator and the frontend never offers filter=3 to non-administrators.

**Actual behavior:** The endpoint returns a JSON response containing all users from ALL organizations in the database, including:
- User UUIDs (`usr_uuid`)
- Login names (`login_name`)
- Email addresses (`member_email`)
- All configured profile fields (names, addresses, phone numbers, etc.)

**Step 3:** Verify that users from Organization B (where the attacker has no membership) appear in the results by checking the `member_this_orga` field — it will be `0` for cross-org users.

## Impact

In multi-organization Admidio deployments (the primary use case for organization isolation), a user manager in one organization can exfiltrate the complete member directory of all other organizations sharing the same database. Exposed data includes:

- Full names and all configured profile fields
- Email addresses
- Login names (useful for credential attacks)
- User UUIDs (useful for targeting other API endpoints)

This completely bypasses the multi-tenant organization isolation boundary. The `contacts_show_all` admin setting (intended to control this feature) is also bypassed, meaning even instances where administrators have explicitly disabled cross-org viewing are affected.

## Recommended Fix

Change line 235 in `modules/contacts/contacts_data.php` to match the frontend guard at `contacts.php:80`:

```php
// Before (vulnerable):
} elseif (($getMembersShowFilter === 3) && $gCurrentUser->isAdministratorUsers()) {

// After (fixed):
} elseif (($getMembersShowFilter === 3) && $gCurrentUser->isAdministrator() && $gSettingsManager->getBool('contacts_show_all')) {
```

Additionally, as defense-in-depth, add an early rejection at the top of the file (after line 59) to block the filter value entirely for unauthorized users:

```php
if ($getMembersShowFilter === 3 && (!$gCurrentUser->isAdministrator() || !$gSettingsManager->getBool('contacts_show_all'))) {
    $getMembersShowFilter = 0; // Fall back to default
}
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-g8p8-94f2-28gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41657
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
