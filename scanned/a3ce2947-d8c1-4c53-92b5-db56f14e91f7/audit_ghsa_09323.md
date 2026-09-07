# [H] phpMyFAQ has stored XSS via Utils::parseUrl() in comment rendering

## Summary
Severity: High
Advisory: GHSA-9525-27vj-c8r8
CVE: CVE-2026-46367
CWE: CWE-116, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-9525-27vj-c8r8
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=4.1.1 <4.1.2
- Packagist: `phpmyfaq/phpmyfaq` — affected >=4.1.1 <4.1.2

## Details
### Summary

A stored XSS vulnerability in the comment rendering pipeline allows an authenticated user to inject JavaScript that executes for every visitor of an affected FAQ or News page. An attacker with a registered account can steal admin session cookies and take over the application.

### Details

`Utils::parseUrl()` (`phpmyfaq/src/phpMyFAQ/Utils.php`, line 281) converts URLs in comment text into clickable `<a>` tags at render time:

    $pattern = '/(https?:\/\/[^\s]+)/i';
    $replacement = '<a href="$1">$1</a>';
    return preg_replace($pattern, $replacement, $string);

The regex `[^\s]+` matches `"` and `<`, and the URL is inserted into the href attribute with no htmlspecialchars() call. A URL with a literal `"` closes the attribute early and allows injecting event handlers like onmouseover.

This only reaches the sink when `main.enableCommentEditor` is enabled. In that path, comment text goes through `sanitizeHtmlComment()` instead of `FILTER_SANITIZE_SPECIAL_CHARS` — which encodes `"` — so the double-quote survives to storage. The comment is then passed through parseUrl() and rendered via `{{ comment.comment|raw }}` in `comment.macros.twig` (line 40), which disables Twig auto-escaping.

The same sink exists in the admin comment panel (`admin/content/comments.twig`, lines 62 and 112), so admins viewing the panel are also affected.

No Content-Security-Policy headers are set anywhere in the app.

### PoC

Requirements:
- main.enableCommentEditor = true (set in admin Configuration panel)
- attacker has any registered user account
- one FAQ entry with comments allowed exists

Steps:
1. Log in as a registered user and open a FAQ with comments.
2. Submit the following as the comment text:

       https://www.evil.com/"onmouseover="alert(document.cookie)

   (www. prefix required — parseUrl strips https:// then only re-adds
   it for www. URLs, which is what triggers the linkification)

3. Any user who views that FAQ page and hovers the link triggers the
   payload. To hit an admin, wait for them to visit the page or check
   the admin comments panel at /admin/content/comments.

Resulting HTML in the page:

    <a href="https://www.evil.com/"onmouseover="alert(document.cookie)">
      ...
    </a>

The `"` closes the href attribute; onmouseover becomes a real attribute.

### Impact

Stored XSS affecting all visitors of the page, including admins. Session cookie theft leads to full admin account takeover. The payload looks like a normal URL and persists until manually deleted.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-9525-27vj-c8r8
- https://nvd.nist.gov/vuln/detail/CVE-2026-46367
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-stored-xss-via-utils-parseurl-in-comment-rendering
