# [M] LiquidJS's strip_html filter bypass via newline characters in HTML tags enables XSS

## Summary
Severity: Medium
Advisory: GHSA-2qv6-9wx5-cwv4
CVE: CVE-2026-44644
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-2qv6-9wx5-cwv4
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0

## Details
## Summary

The `strip_html` filter in liquidjs is intended to remove HTML tags from a string before rendering, and is widely used as an XSS sanitizer. The implementation uses a regex whose catch-all branch (`<.*?>`) does not match line terminators, so any HTML tag containing a `\n` or `\r` character passes through unmodified. An attacker who can place a newline inside a tag (e.g. `<img\nsrc=x\nonerror=alert(1)>`) bypasses sanitization entirely, since browsers treat newlines as whitespace within a tag and execute the resulting `onerror`/`onload`/etc. handler. This results in stored or reflected XSS in any application that relies on `strip_html` to neutralize untrusted HTML.

## Details

The vulnerable code is in `src/filters/html.ts`:

```ts
// src/filters/html.ts:45-49
export function strip_html (this: FilterImpl, v: string) {
  const str = stringify(v)
  this.context.memoryLimit.use(str.length)
  return str.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<.*?>|<!--[\s\S]*?-->/g, '')
}
```

The regex has four alternations:
1. `<script[\s\S]*?<\/script>` — uses `[\s\S]`, matches across newlines.
2. `<style[\s\S]*?<\/style>` — uses `[\s\S]`, matches across newlines.
3. `<.*?>` — uses `.`, which in JavaScript does **not** match `\n` or `\r` (no `s`/dotAll flag set).
4. `<!--[\s\S]*?-->` — uses `[\s\S]`, matches across newlines.

Branch 3 is the catch-all for "any other tag." Because `.` excludes line terminators, a tag containing a newline does not match any alternative. The literal characters of the tag are passed through to the output.

Browsers, however, parse HTML tag content with whitespace tolerance: per the HTML spec, attribute names and values may be separated by ASCII whitespace, which includes `\n` and `\r`. So `<img\nsrc=x\nonerror=alert(1)>` is parsed as a valid `img` element with an `onerror` handler.

`liquidjs`' default rendering pipeline does not auto-escape filter output (the `outputEscape` engine option is undefined by default — see `src/liquid-options.ts`), so the unescaped HTML is delivered verbatim to the consumer's HTML response.

Trust path:
- Application receives untrusted input (e.g. user comment field).
- Developer renders it as `{{ comment | strip_html }}` to "safely" embed user content as plaintext.
- Attacker submits `<img\u000Asrc=x\u000Aonerror=alert(document.cookie)>`.
- `strip_html` returns the input unchanged.
- Output is written into the HTML response with no further escaping.
- Victim's browser executes the attacker's JavaScript in the application's origin.

This is an inconsistency bug: the same regex correctly uses `[\s\S]` for `<script>`, `<style>`, and comment branches, but reverts to `.` for the catch-all. The other branches' authors clearly knew to handle multi-line content; the catch-all was missed.

## PoC

Reproduces against current HEAD (10.25.7) using the published `dist/liquid.node.js` build:

```bash
node -e "
const { Liquid } = require('./dist/liquid.node.js');
const engine = new Liquid();
engine.parseAndRender(
  'Safe output: {{ input | strip_html }}',
  { input: '<img\nsrc=x\nonerror=\"alert(document.cookie)\">' }
).then(r => console.log(JSON.stringify(r)));
"
```

Verified output:

```
"Safe output: <img\nsrc=x\nonerror=\"alert(document.cookie)\">"
```

The `<img ... onerror=...>` tag is delivered to the output completely unmodified. When this string is placed into an HTML document and parsed by a browser, the `onerror` handler executes.

Same bypass works with `\r` (carriage return), `\r\n`, or any combination of CR/LF inside the tag. It also works with other event-handler vectors (`<svg\nonload=alert(1)>`, `<body\nonload=alert(1)>`, `<iframe\nsrc="javascript:alert(1)">`, etc.) and is not specific to `<img>`.

For comparison, the same input without a newline is correctly stripped:

```bash
node -e "
const { Liquid } = require('./dist/liquid.node.js');
const engine = new Liquid();
engine.parseAndRender(
  'Safe output: {{ input | strip_html }}',
  { input: '<img src=x onerror=\"alert(1)\">' }
).then(r => console.log(JSON.stringify(r)));
"
# → "Safe output: "
```

This confirms `strip_html` is intended to remove tags of this shape, and the newline form is a sanitizer bypass rather than expected behavior.

## Impact

Any liquidjs-using application that:
1. Renders attacker-controlled strings via `{{ x | strip_html }}` to defend against HTML injection, AND
2. Does not separately HTML-escape that output (default behavior — `outputEscape` is unset by default),

Is vulnerable to stored or reflected XSS. The attacker can execute arbitrary JavaScript in the victim's browser in the application's origin, enabling session theft, account takeover, CSRF with origin-scoped credentials, and arbitrary actions in the victim's authenticated session. The XSS is triggered with simple, well-known event-handler payloads — no exotic encoding, no character set tricks, just a literal newline inside the tag.

The blast radius matches the deployment of liquidjs as a server-side template engine: liquidjs is one of the most popular Liquid implementations on npm (millions of downloads/week) and `strip_html` is documented as the sanitization filter for HTML stripping, so the vulnerable pattern (`{{ user | strip_html }}`) is the natural and recommended use of the filter.

## Recommended Fix

Replace `<.*?>` with `<[\s\S]*?>` (or apply the `s`/dotAll flag to the entire regex) so the catch-all branch matches across line terminators, consistent with the other branches:

```ts
// src/filters/html.ts
export function strip_html (this: FilterImpl, v: string) {
  const str = stringify(v)
  this.context.memoryLimit.use(str.length)
  return str.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<[\s\S]*?>|<!--[\s\S]*?-->/g, '')
}
```

Equivalent fix using the dotAll flag (requires ES2018+, which liquidjs already targets):

```ts
return str.replace(/<script.*?<\/script>|<style.*?<\/style>|<.*?>|<!--.*?-->/gs, '')
```

After the fix, the PoC input is correctly reduced to an empty string. Note that `strip_html` should still not be relied on as a primary XSS defense — the project README/documentation should recommend HTML-escaping (`escape` filter) for untrusted content rendered into HTML contexts. A brief security note in the filter's documentation would help users who currently treat `strip_html` as a sanitizer.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-2qv6-9wx5-cwv4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44644
- https://github.com/harttle/liquidjs/commit/26ea2856c7a90aec892b98d94a9b7a3e18539045
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.26.0
