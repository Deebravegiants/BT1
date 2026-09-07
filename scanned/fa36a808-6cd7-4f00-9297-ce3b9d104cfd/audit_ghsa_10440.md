# [M] Admidio vulnerable to reflected XSS in msg_window.php via Square Bracket to HTML Tag Conversion

## Summary
Severity: Medium
Advisory: GHSA-gq27-fc8w-vcmp
CVE: CVE-2026-41661
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-gq27-fc8w-vcmp
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

An unauthenticated attacker can execute arbitrary JavaScript in any Admidio user's browser through a reflected XSS in `system/msg_window.php`. The endpoint passes user input through `htmlspecialchars()`, which does not encode square brackets. A subsequent call to `Language::prepareTextPlaceholders()` converts those brackets into HTML angle brackets, producing executable markup.

## Details

The `msg_window.php` endpoint accepts `message_id` and `message_var1` as GET parameters. At line 146, the code passes `message_var1` through `htmlspecialchars()` before inserting it into the language string as a placeholder:

```php
// system/msg_window.php:146
$messageText = $gL10n->get($messageId, array(htmlspecialchars($messageVar1)));
```

`htmlspecialchars()` encodes `<`, `>`, `&`, `"`, and `'` but leaves `[` and `]` untouched. The `Language::get()` method calls `Language::prepareTextPlaceholders()`, which performs a character-level translation:

```php
// src/Infrastructure/Language.php:497
$text = strtr($text, '[]', '<>');
```

This converts all square brackets in the output string, including those from user input, into angle brackets. An attacker submits `[script]alert(document.domain)[/script]`, which survives `htmlspecialchars()` unchanged, then becomes `<script>alert(document.domain)</script>` after placeholder preparation.

The application sets no Content-Security-Policy headers, so inline scripts execute without restriction.

## Proof of Concept

Visit the following URL on any Admidio installation (no authentication required):

```
https://<admidio-host>/system/msg_window.php?message_id=INS_INSTALLATION_VERSION&message_var1=%5Bscript%5Dalert(document.domain)%5B/script%5D
```

The server responds with an HTML page containing:

```html
Installation version <script>alert(document.domain)</script>
```

The JavaScript executes in the context of the Admidio origin, displaying the current domain in an alert dialog.

## Impact

An attacker crafts a malicious URL and sends it to any Admidio user. When the victim clicks the link, attacker-controlled JavaScript runs in their browser session. The attacker can steal session cookies, perform administrative operations on behalf of the victim, or redirect the victim to phishing pages. The endpoint requires no authentication.

## Recommended Fix

Apply output encoding after `Language::prepareTextPlaceholders()` runs, or stop translating square brackets that originate from user-supplied placeholder values. A targeted fix: escape `[` and `]` in user input before passing it into `Language::get()`.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-gq27-fc8w-vcmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-41661
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
