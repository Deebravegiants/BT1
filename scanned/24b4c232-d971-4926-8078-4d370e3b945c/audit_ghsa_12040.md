# [M] AVideo has Unauthenticated Information Disclosure of User Group Permission Mappings via Permissions Plugin

## Summary
Severity: Medium
Advisory: GHSA-96qp-8cmq-jvq8
CVE: CVE-2026-33501
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-96qp-8cmq-jvq8
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The endpoint `plugin/Permissions/View/Users_groups_permissions/list.json.php` lacks any authentication or authorization check, allowing unauthenticated users to retrieve the complete permission matrix mapping user groups to plugins. All sibling endpoints in the same directory (`add.json.php`, `delete.json.php`, `index.php`) properly require `User::isAdmin()`, indicating this is an oversight.

## Details

The vulnerable file at `plugin/Permissions/View/Users_groups_permissions/list.json.php:1-7` contains:

```php
<?php
require_once '../../../../videos/configuration.php';
require_once $global['systemRootPath'] . 'plugin/Permissions/Objects/Users_groups_permissions.php';
header('Content-Type: application/json');

$rows = Users_groups_permissions::getAll();
?>
{"data": <?php echo json_encode($rows); ?>}
```

This calls `ObjectYPT::getAll()` (defined in `objects/Object.php:98-111`), which executes:

```php
$sql = "SELECT * FROM  " . static::getTableName() . " WHERE 1=1 ";
$sql .= self::getSqlFromPost();
```

This returns all rows from the `users_groups_permissions` table as JSON with no access control.

Compare with the sibling `add.json.php:10-15` and `delete.json.php:9-14`, which both enforce:

```php
$plugin = AVideoPlugin::loadPluginIfEnabled('Permissions');
if(!User::isAdmin()){
    $obj->msg = "You cant do this";
    die(json_encode($obj));
}
```

Similarly, `index.php:6-8` (the admin page that loads this data via AJAX) checks:

```php
if (!User::isAdmin()) {
    forbiddenPage("You can not do this");
    exit;
}
```

No `.htaccess` or web server configuration restricts direct access to this endpoint.

## PoC

```bash
# Retrieve complete permission mappings without authentication
curl -s https://target/plugin/Permissions/View/Users_groups_permissions/list.json.php
```

**Expected response (admin-only data):**
```json
{"data": [{"id":"1","name":null,"users_groups_id":"2","plugins_id":"5","type":"1","status":"a"}, ...]}
```

Each row reveals:
- `users_groups_id` — numeric ID of a user group
- `plugins_id` — numeric ID of an installed plugin
- `type` — the permission level granted
- `status` — whether the permission is active (`a`) or inactive

The `getSqlFromPost()` method also processes `$_POST['sort']` and `$_GET` parameters, allowing an attacker to paginate and sort results to extract all data systematically.

## Impact

An unauthenticated attacker can enumerate the complete authorization model of the AVideo instance:

- **All user group IDs** and which plugins each group can access
- **All installed plugin IDs** and their permission configurations
- **Permission types and active/inactive status** for each group-plugin pair

This information provides a detailed roadmap of the application's authorization architecture, significantly aiding targeted privilege escalation, as an attacker would know exactly which groups have access to which plugins and what permission types are assigned. While not directly exploitable for data modification, it reduces the attacker's effort for follow-up attacks.

## Recommended Fix

Add the same admin authorization check used by the sibling endpoints. In `plugin/Permissions/View/Users_groups_permissions/list.json.php`:

```php
<?php
require_once '../../../../videos/configuration.php';
require_once $global['systemRootPath'] . 'plugin/Permissions/Objects/Users_groups_permissions.php';
header('Content-Type: application/json');

$plugin = AVideoPlugin::loadPluginIfEnabled('Permissions');
if(!User::isAdmin()){
    die(json_encode(['error' => true, 'msg' => 'You cant do this']));
}

$rows = Users_groups_permissions::getAll();
?>
{"data": <?php echo json_encode($rows); ?>}
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-96qp-8cmq-jvq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33501
- https://github.com/WWBN/AVideo/commit/b583acdc9a9d1eab461543caa363e1a104fb4516
- https://github.com/WWBN/AVideo/commit/dc3c825734628bb32550d0daa125f05bacb6829c
- https://github.com/WWBN/AVideo
