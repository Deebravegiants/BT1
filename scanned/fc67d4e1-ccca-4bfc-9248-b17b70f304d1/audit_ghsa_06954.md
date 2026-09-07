# [H] NukeViet: Multiple Anti-XSS Filter Bypasses Leading to Stored XSS in News Module

## Summary
Severity: High
Advisory: GHSA-465g-4q99-5x86
CVE: CVE-2026-54064
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-465g-4q99-5x86
Type: github-advisory

## Affected
- Packagist: `nukeviet/nukeviet` — affected >=0 <4.6.00

## Details
## Summary

Two filter-bypass techniques in `NukeViet\Core\Request::filterAttr()` and `NukeViet\Core\Request::unhtmlentities()` allow a low-privileged user (any account with news post permission) to store and serve arbitrary JavaScript to any visitor of the affected page.

## Affected Component

`vendor/vinades/nukeviet/Core/Request.php` — class `NukeViet\Core\Request`

## Vulnerability Details

### Bypass 1 — Form Feed character prefix (`\x0C`) before event handler name

The `filterAttr()` method blocks event-handler attributes using:
```php
preg_match('/^on/i', $attrSubSet[0])
```
PHP's `trim()` does **not** strip the ASCII Form Feed character (`\x0C`, U+000C). An attacker can prefix the attribute name with `\x0C` so that `\x0Conerror` does not match `/^on/`. The HTML5 browser parser treats `\x0C` as a valid whitespace separator and correctly activates the event handler.

**Proof-of-concept payload (URL-encoded POST body field `bodyhtml`):**
```
<img src="x" %0Conerror="alert('XSS')">
```

### Bypass 2 — Decimal HTML entity tab (`&#9;`) inside `javascript:` URI

`unhtmlentities()` strips the hex-encoded tab `&#x09;` via `str_ireplace`, but did **not** strip its decimal equivalent `&#9;`. The keyword-blocking regex `/j\s*a\s*v\s*a\s*s\s*c\s*r\s*i\s*p\s*t/si` uses `\s*` which does not match HTML entities. The value `jav&#9;ascript:alert()` passes the filter, is stored in the database, and is decoded by the browser into a working `javascript:` URI.

**Proof-of-concept payload (inside a Markdown-style link):**
```
[Click me](jav&#9;ascript:alert('XSS'))
```

## Impact

An authenticated attacker with news-posting permission can inject persistent JavaScript that executes in the browser of **any user** (including administrators) who views the affected article. This enables session cookie theft, credential harvesting, defacement, and further privilege escalation.

## Patches

Fixed in commit `<commit-sha>` by modifying `vendor/vinades/nukeviet/Core/Request.php`:

1. **`filterAttr()`** — strip all ASCII control characters (`\x00`–`\x20`) from the attribute name before the `/^on/` check:
   ```php
   $attrSubSet[0] = preg_replace('/[\x00-\x20]/', '', strtolower($attrSubSet[0]));
   ```

2. **`unhtmlentities()`** — strip decimal HTML entities for all ASCII control characters (0–31) before the keyword checks:
   ```php
   $value = preg_replace('/&#0*(?:3[01]|[12][0-9]|[0-9]);/', '', $value);
   ```

## Workarounds

None. Update to the patched version.

## Resources

- CWE-79: Improper Neutralization of Input During Web Page Generation (Cross-site Scripting)
- OWASP WSTG-INPV-02: Testing for Stored Cross Site Scripting
- [OWASP Top 10 A03:2021 – Injection](https://owasp.org/Top10/A03_2021-Injection/)

## References
- https://github.com/nukeviet/nukeviet/security/advisories/GHSA-465g-4q99-5x86
- https://github.com/nukeviet/nukeviet
