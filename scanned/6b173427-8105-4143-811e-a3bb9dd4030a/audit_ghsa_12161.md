# [M] CraftCMS vulnerable to reflective XSS via incomplete return URL sanitization

## Summary
Severity: Medium
Advisory: GHSA-fvwq-45qv-xvhv
CVE: CVE-2026-31859
CWE: CWE-116, CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-fvwq-45qv-xvhv
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.15.3 <4.17.3
- Packagist: `craftcms/cms` — affected >=5.7.5 <5.9.7

## Details
### Summary

The fix for CVE-2025-35939 in `craftcms/cms` introduced a `strip_tags()` call in `src/web/User.php` to sanitize return URLs before they are stored in the session. However, `strip_tags()` only removes HTML tags (angle brackets) -- it does not inspect or filter URL schemes. Payloads like `javascript:alert(document.cookie)` contain no HTML tags and pass through `strip_tags()` completely unmodified, enabling reflected XSS when the return URL is rendered in an `href` attribute.

### Details
The patched code in is:

```php
public function setReturnUrl($url): void
{
    parent::setReturnUrl(strip_tags($url));
}
```

`strip_tags()` removes HTML tags (e.g., `<script>`, `<img>`) from a string, but it is **not** a URL sanitizer. When the sanitized return URL is subsequently rendered in an `href` attribute context (e.g., `<a href="{{ returnUrl }}">`), the following dangerous payloads survive `strip_tags()` completely unmodified:

1. **`javascript:` protocol URLs** -- `javascript:alert(document.cookie)` contains no HTML tags, so `strip_tags()` returns it verbatim. When placed in an `href`, clicking the link executes the JavaScript.

2. **`data:` URIs** -- `data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==` uses Base64 encoding and contains no tags at all, bypassing `strip_tags()` entirely.

3. **Protocol-relative URLs** -- `//evil.com/steal` contains no tags and is passed through unchanged. When rendered as an `href`, the browser resolves it relative to the current page’s protocol, redirecting the user to an attacker-controlled domain.

The core issue is that `strip_tags()` operates on HTML syntax (angle brackets) while the threat model here requires URL scheme validation. These are fundamentally different security concerns.

### Impact

**Reflected XSS via crafted return URL.** An attacker constructs a malicious link such as `https://target.example.com/craft/?returnUrl=javascript:alert(document.cookie)` and sends it to a victim. The attack flow is:

1. Victim clicks the link, visiting the Craft CMS site.
2. The application calls `setReturnUrl()` with the attacker-controlled value.
3. `strip_tags()` processes the URL but finds no HTML tags -- it passes through unchanged.
4. The URL is stored in the session and later rendered in an `href` attribute (e.g., a "Return" or "Continue" link).
5. When the victim clicks that link, `javascript:alert(document.cookie)` executes in the context of the Craft CMS origin.

This enables:
- **Session hijacking** via cookie theft (`document.cookie`)
- **Data exfiltration** via `fetch()` to an attacker-controlled server
- **Phishing** by redirecting to a lookalike domain (protocol-relative URL)
- **CSRF** by performing actions on behalf of the authenticated user

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-fvwq-45qv-xvhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-31859
- https://github.com/craftcms/cms/commit/cc9921c14897ee2b592a431c2356af8a04ce4cfe
- https://github.com/craftcms/cms
