# [M] Marko: XSS via case-insensitive script/style closing tag bypass in runtime HTML escaping

## Summary
Severity: Medium
Advisory: GHSA-x9fj-57fh-c8wq
CVE: CVE-2026-41591
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-x9fj-57fh-c8wq
Type: github-advisory

## Affected
- npm: `marko` — affected >=0 <5.38.36
- npm: `@marko/runtime-tags` — affected >=0 <6.0.164

## Details
### Summary

When dynamic text is interpolated into a `<script>` or `<style>` tag the Marko runtime failed to prevent tag breakout when the closing tag used non-lowercase casing.
An attacker able to place input inside a `<script>` or `<style>` block could break out of the tag with `</SCRIPT>`, `</Style>`, etc. and inject arbitrary HTML/JavaScript, resulting in cross-site scripting.

### Details

The affected helpers used case-sensitive regular expressions to detect attempts at closing the surrounding tag:

```js
// packages/runtime-tags/src/html/content.ts
const unsafeScriptReg = /<\/script/g;
const unsafeStyleReg  = /<\/style/g;

// packages/runtime-class/src/runtime/html/helpers/escape-script-placeholder.js
const unsafeCharsReg = /<\/script/g;

// packages/runtime-class/src/runtime/html/helpers/escape-style-placeholder.js
const unsafeCharsReg = /<\/style/g;
```

HTML tag names are case-insensitive in the browser parser, so inputs such as `</SCRIPT>`, `</Script>`, or `</sTyLe>` were not matched by these regexes and passed through the helpers unchanged. A browser rendering the output treats the mixed-case end tag as a valid closing tag, terminating the script or style context, and then parses anything that follows as HTML.

The Marko compiler routes interpolated values inside `<script>` and `<style>` tags through these helpers automatically (see `native-tag.ts:1080-1085`), so application code following the framework's conventions had no way to detect or compensate for the gap.

### PoC

```marko
$ const userCode = "</SCRIPT><script>alert(1)//";
<script>
  const data = ${JSON.stringify(userCode)};
</script>
```

Would yield the following:

```html
<script>const data = "</SCRIPT><script>alert(1)//";</script>
```

Which is then parsed in any WHATWG-compliant browser as:
```html
<script>const data = "</script>
<script>alert(1)//";</script>
```

### Impact

Cross-site scripting. Any Marko template that explicitly interpolates untrusted data inside a `<script>` or `<style>` block is affected.

Stored XSS is trivial if the value originates from any persisted user input (username, profile bio, comment body, etc.) that is later embedded in a script tag during rendering. Exploitation yields arbitrary JavaScript execution in the victim's browser, enabling session token theft, account takeover, and arbitrary actions as the victim.

Since the internal `_escape_script` and `_escape_style` helpers are the framework's designated defense against script/style tag breakout, applications following standard Marko patterns had no obvious reason to add a second layer of sanitization.

This does not affect scripts or hydration state serialized by Marko itself — only templates that explicitly interpolate untrusted values inside a <script> or <style> tag.

### Patch

Commit `19d4b37d0` — `fix: html script, style, and comment escaping`.

```diff
- const unsafeScriptReg = /<\/script/g;
+ const unsafeScriptReg = /<\/script/gi;

- const unsafeStyleReg  = /<\/style/g;
+ const unsafeStyleReg  = /<\/style/gi;
```

The same commit also introduced an `_escape_comment` helper and corresponding `escape-comment-placeholder.js`, hardening HTML comment escaping as a related preventative fix. Test fixtures were added under `escape-script-case`, `escape-style-case`, and `escape-comment`.

### Workarounds

Upgrade to the patched release. As a short-term mitigation on affected versions, pre-sanitize any untrusted data before it reaches a template position rendered inside a `<script>` or `<style>` tag — e.g. normalize `</script`, `</style`, and their mixed-case variants before interpolation, or avoid direct interpolation of untrusted values inside these tags entirely.

## References
- https://github.com/marko-js/marko/security/advisories/GHSA-x9fj-57fh-c8wq
- https://nvd.nist.gov/vuln/detail/CVE-2026-41591
- https://github.com/marko-js/marko
