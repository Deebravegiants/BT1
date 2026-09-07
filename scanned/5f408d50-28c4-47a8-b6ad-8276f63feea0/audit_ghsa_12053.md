# [M] AVideo has Reflected XSS via unlockPassword Parameter in forbiddenPage.php and warningPage.php

## Summary
Severity: Medium
Advisory: GHSA-7292-w8qp-mhq2
CVE: CVE-2026-33499
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-7292-w8qp-mhq2
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `view/forbiddenPage.php` and `view/warningPage.php` templates reflect the `$_REQUEST['unlockPassword']` parameter directly into an HTML `<input>` tag's attributes without any output encoding or sanitization. An attacker can craft a URL that breaks out of the `value` attribute and injects arbitrary HTML attributes including JavaScript event handlers, achieving reflected XSS against any visitor who clicks the link.

## Details

When a user visits a password-protected channel, `view/channel.php:22` calls:
```php
forbiddenPage('This channel is password protected', false, $channelPassword);
```

The `forbiddenPage()` function in `objects/functionsSecurity.php:520` checks whether the supplied password matches. If it doesn't (or no password was submitted), it includes `view/forbiddenPage.php` at line 561.

In `view/forbiddenPage.php:31-35`, the raw request parameter is reflected into HTML:
```php
$value = '';
if (!empty($_REQUEST['unlockPassword'])) {
    $value = $_REQUEST['unlockPassword'];  // Line 33: unsanitized user input
}
echo getInputPassword('unlockPassword', 'class="form-control" value="' . $value . '"', __('Unlock Password'));
```

The `getInputPassword()` function at `objects/functions.php:4490` outputs the `$attributes` string directly into the `<input>` tag at line 4502:
```php
<input id="<?php echo $id; ?>" name="<?php echo $id; ?>" type="password" placeholder="<?php echo $placeholder; ?>" <?php echo $attributes; ?>>
```

The `unlockPassword` parameter is **not listed** in any of the security filter arrays defined in `objects/security.php:4-8` (`$securityFilter`, `$securityFilterInt`, `$securityRemoveSingleQuotes`, `$securityRemoveNonChars`, `$securityRemoveNonCharsStrict`, `$filterURL`), so it passes through the global input sanitization completely unfiltered.

Commit `3933d4abc` added sanitization only for the server-side password **comparison** in `functionsSecurity.php:529` (`preg_replace('/[^0-9a-z]/i', '', ...)`), but did not address the client-side reflection in the view templates.

The identical vulnerability exists in `view/warningPage.php:31-34`.

## PoC

**Step 1:** Identify a password-protected channel (or any page that triggers `forbiddenPage()` with an `$unlockPassword`).

**Step 2:** Craft a URL with a malicious `unlockPassword` parameter that breaks out of the `value` attribute:

```
https://target.com/channel/someuser?unlockPassword=" autofocus onfocus="alert(document.cookie)
```

**Step 3:** The server renders the following HTML:

```html
<input id="unlockPassword" name="unlockPassword" type="password"
  placeholder="Unlock Password"
  class="form-control" value="" autofocus onfocus="alert(document.cookie)">
```

The `autofocus` attribute causes the browser to immediately focus the input element on page load, triggering the `onfocus` event handler which executes the attacker-controlled JavaScript. No further user interaction is required beyond clicking the link.

**Step 4:** The JavaScript executes in the context of the target domain, with access to cookies (no CSP or HttpOnly protections were observed), DOM, and the ability to make authenticated requests on behalf of the victim.

## Impact

- **Session hijacking**: An attacker can steal `PHPSESSID` cookies and impersonate any user (including administrators) who clicks the crafted link.
- **Account takeover**: The injected JavaScript can change the victim's email/password by submitting forms to the application's account settings endpoints.
- **Phishing**: The attacker can overlay fake login forms or redirect users to credential harvesting pages.
- **No authentication required**: The vulnerable page is specifically shown to unauthenticated/unauthorized users, making the attack surface broad.

## Recommended Fix

Apply `htmlspecialchars()` output encoding to the reflected value in both `view/forbiddenPage.php` and `view/warningPage.php`:

**view/forbiddenPage.php** — change line 33:
```php
// Before (vulnerable):
$value = $_REQUEST['unlockPassword'];

// After (fixed):
$value = htmlspecialchars($_REQUEST['unlockPassword'], ENT_QUOTES, 'UTF-8');
```

**view/warningPage.php** — change line 32:
```php
// Before (vulnerable):
$value = $_REQUEST['unlockPassword'];

// After (fixed):
$value = htmlspecialchars($_REQUEST['unlockPassword'], ENT_QUOTES, 'UTF-8');
```

Alternatively, add `'unlockPassword'` to the `$securityFilter` array in `objects/security.php:4` to apply the global XSS filter, though explicit output encoding at the point of use is the more robust defense-in-depth approach.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-7292-w8qp-mhq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33499
- https://github.com/WWBN/AVideo/commit/f154167251c9cf183ce09cd018d07e9352310457
- https://github.com/WWBN/AVideo
