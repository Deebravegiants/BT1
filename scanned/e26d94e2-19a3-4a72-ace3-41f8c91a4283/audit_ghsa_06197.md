# [M] Snipe-IT has an authorization bypass on print inventory page

## Summary
Severity: Medium
Advisory: GHSA-fc33-6w3q-538h
CVE: CVE-2026-55462
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-fc33-6w3q-538h
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.1

## Details
### Impact
An authenticated user with only `users.view` can open another user's detail page and see assigned license, accessory, and consumable data even though the same account is denied direct access to the Licenses, Accessories, and Consumables modules. The leaked data includes software license names, purchase order/order values, accessory and consumable names, assignment notes, and purchase costs.

### Attacker Model

Authenticated user with only:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ json
{"users.view":"1"}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The attacker does not have:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ json
{
  "licenses.view": "1",
  "accessories.view": "1",
  "consumables.view": "1",
  "assets.view": "1"
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Affected Component

-   `app/Http/Controllers/Users/UsersController.php`

-   `resources/views/users/view.blade.php`

-   `resources/views/users/print.blade.php`

-   Endpoints:

    -   `GET /users/{user}`

    -   `GET /users/{user}/print`

### Root Cause

`UsersController::show()` authorizes only viewing the user, then loads inventory relationships:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ php
$this->authorize('view', $user);

$user = User::with([
    'consumables',
    'accessories',
    'licenses',
    'userloc',
    'groups',
])
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`resources/views/users/view.blade.php` renders those relationships without checking the corresponding module permissions. The license table renders name, purchase cost, purchase order, and order number. The accessory and consumable tables render item names, notes, and unit costs.

`UsersController::printInventory()` similarly authorizes only `view` on `User::class` and the target user, then renders `resources/views/users/print.blade.php`, which outputs assigned inventory names.

### Proof of Concept

1.  Create a user with only `users.view`.

2.  Create a target user with assigned license/accessory/consumable records containing recognizable test values.

3.  Log in as the `users.view`-only user.

4.  Confirm direct module access is denied:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ http
GET /licenses
GET /accessories
GET /consumables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Observed for each:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ http
HTTP/1.1 403 Forbidden
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  Request the target user's page:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ http
GET /users/<target-user-id> HTTP/1.1
Host: <snipe-it-host>
Cookie: snipeit_session=<attacker-session>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Observed:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ http
HTTP/1.1 200 OK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The response contained assigned inventory data from modules the attacker could not directly access, including license name, purchase order/order values, accessory name/note/cost, and consumable name/note/cost.

1.  Request the print view:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ http
GET /users/<target-user-id>/print HTTP/1.1
Host: <snipe-it-host>
Cookie: snipeit_session=<attacker-session>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Observed:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ http
HTTP/1.1 200 OK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The response contained assigned inventory names.

### Evidence

The `users.view`-only test account was confirmed to lack direct inventory permissions:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ json
{
  "has_users_view": true,
  "has_licenses_view": false,
  "has_accessories_view": false,
  "has_consumables_view": false,
  "has_assets_view": false
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Direct access to `/licenses`, `/accessories`, and `/consumables` returned `403 Forbidden`.

The same account received `200 OK` from `/users/<target-user-id>` and the response included assigned inventory data that should have been protected by the corresponding inventory module permissions.

### Negative Controls

Denied direct module responses did not include the test inventory strings. The same data was only disclosed through the user detail and user print views.

### Impact

Organizations may use separate permissions to allow HR/helpdesk-style users to view people records without exposing license, accessory, or consumable inventories and cost/order metadata. This issue bypasses those module-specific permissions and leaks assigned inventory information through the user view.


### Patches
Patched in 374f426f0c

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-fc33-6w3q-538h
- https://nvd.nist.gov/vuln/detail/CVE-2026-55462
- https://github.com/grokability/snipe-it/commit/374f426f0c6bb7a4f129f7b85051cc1da753a0f5
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
